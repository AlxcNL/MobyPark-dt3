from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app import models
from app.security import check_token

DEFAULT_LIMIT = 50
MAX_LIMIT = 200

bearer_scheme = HTTPBearer(auto_error=True)

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
):
    print(creds)
    user_id = check_token(creds.credentials)
    result = await db.execute(select(models.User).where(models.User.id == user_id))
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

def calculate_price(parking_lot: models.ParkingLot, start: datetime, stop: Optional[datetime] = None):
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

def generate_payment_hash(sid, vehicle: schemas.VehicleBase):
    return md5(str(sid + vehicle.license_plate).encode("utf-8")).hexdigest()

