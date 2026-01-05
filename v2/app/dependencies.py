from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Query
from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .database import get_db
from .models import User, ParkingLot, Payment
from .schemas import VehicleBase
from .security import check_token

from typing import Optional
from datetime import datetime, timezone

import re
import math
from hashlib import md5
import uuid

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

bearer_scheme = HTTPBearer(auto_error=True)

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    print(creds)
    user_id = check_token(creds.credentials)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

class PageParams(BaseModel):
    limit: int
    offset: int

def page_params(
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
) -> PageParams:
    return PageParams(limit=limit, offset=offset)

def calculate_price(parking_lot: ParkingLot, start: datetime, stop: Optional[datetime] = None):
    if stop is None:
        stop = datetime.now(timezone.utc)

    # ensure both aware UTC
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    else:
        start = start.astimezone(timezone.utc)
    stop = stop.astimezone(timezone.utc)

    diff = stop - start
    seconds = diff.total_seconds()
    hours = int(math.ceil(seconds / 3600.0))

    if parking_lot.tariff < 0 or parking_lot.daytariff < 0:
        raise ValueError("Negative value is not possible")
    # coerce tariffs
    t = float(parking_lot.tariff) if parking_lot.tariff is not None else 0.0
    dtf = float(parking_lot.daytariff) if parking_lot.daytariff is not None else 999.0

    if seconds < 180:
        price = 0.0
        days = 0
    elif stop.date() > start.date():
        days = diff.days + 1
        price = dtf * days
    else:
        days = 0
        price = min(t * hours, dtf)

    return (round(price, 2), hours, days)

def generate_payment_hash(sid, vehicle: VehicleBase):
    return md5(str(sid + vehicle.license_plate).encode("utf-8")).hexdigest()

def generate_transaction_validation_hash():
    return str(uuid.uuid4())

def tr_hash(session_id: int, license_plate: str) -> str:
    # match legacy transaction key (md5 of sid + licenseplate)
    base = f"{session_id}{license_plate}"
    return md5(base.encode("utf-8")).hexdigest()

async def sum_paid_eur(db: AsyncSession, session_id: int, thash: str) -> float:
    # Prefer summing by session_id (new schema). If 0, fall back to legacy 'hash' column.
    res = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.sessions_id == session_id
        )
    )
    cents = res.scalar_one() or 0
    if cents:
        return round(cents / 100.0, 2)

    res = await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.hash == thash
        )
    )
    cents = res.scalar_one() or 0
    return round(cents / 100.0, 2)

def licenceplate_clean(license_plate: str) -> str:
    """Clean license plate by removing spaces, dashes and converting to uppercase."""
    if not license_plate:
        return ""
    # Remove spaces, dashes, and other common separators, convert to uppercase
    cleaned = re.sub(r'[\s\-]', '', license_plate).upper()
    return cleaned