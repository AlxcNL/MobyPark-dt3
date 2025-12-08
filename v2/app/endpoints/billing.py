from __future__ import annotations

import hashlib
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, check_token, calculate_price, tr_hash, sum_paid_eur
from app.security import require_admin

router = APIRouter(prefix="", tags=["billing"])
bearer_scheme = HTTPBearer(auto_error=True)

@router.get("/billing", response_model=schemas.BillingSummary)
async def billing_summary_me(
    db: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: models.User = Depends(get_current_user),
):
    check_token(token.credentials)

    # Sessions belonging to the user's vehicles, with lot + vehicle
    q = (
        select(models.Session, models.ParkingLot, models.Vehicle)
        .join(models.Vehicle, models.Session.vehicles_id == models.Vehicle.id)
        .join(models.ParkingLot, models.Session.parking_lots_id == models.ParkingLot.id)
        .where(models.Vehicle.users_id == current_user.id)
    )
    res = await db.execute(q)
    rows = res.all()  # list[(Session, ParkingLot, Vehicle)]

    total_amount = 0.0
    total_paid = 0.0
    sessions_count = 0

    for s, lot, veh in rows:
        # compute amount per legacy rules (returns euros)
        amount_eur, _hours, _days = calculate_price(lot, s.start_date, s.stop_date)
        thash = tr_hash(s.id, veh.license_plate)
        paid_eur = await sum_paid_eur(db, s.id, thash)

        total_amount += amount_eur
        total_paid += paid_eur
        sessions_count += 1

    total_amount = round(total_amount, 2)
    total_paid = round(total_paid, 2)
    balance = round(total_amount - total_paid, 2)
    average = round(total_amount / sessions_count, 2) if sessions_count else 0.0

    return schemas.BillingSummary(
        amount=total_amount,
        payed=total_paid,       # keep legacy spelling
        balance=balance,
        sessions=sessions_count,
        average=average,
    )


@router.get("/billing/{uid}", response_model=schemas.BillingSummary)
async def billing_summary_user(
    uid: int,
    db: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: models.User = Depends(get_current_user),
):
    check_token(token.credentials)
    require_admin(current_user)

    q = (
        select(models.Session, models.ParkingLot, models.Vehicle)
        .join(models.Vehicle, models.Session.vehicles_id == models.Vehicle.id)
        .join(models.ParkingLot, models.Session.parking_lots_id == models.ParkingLot.id)
        .where(models.Vehicle.users_id == uid)
    )
    res = await db.execute(q)
    rows = res.all()

    total_amount = 0.0
    total_paid = 0.0
    sessions_count = 0

    for s, lot, veh in rows:
        amount_eur, _hours, _days = calculate_price(lot, s.start_date, s.stop_date)
        thash = tr_hash(s.id, veh.license_plate)
        paid_eur = await sum_paid_eur(db, s.id, thash)

        total_amount += amount_eur
        total_paid += paid_eur
        sessions_count += 1

    total_amount = round(total_amount, 2)
    total_paid = round(total_paid, 2)
    balance = round(total_amount - total_paid, 2)
    average = round(total_amount / sessions_count, 2) if sessions_count else 0.0

    return schemas.BillingSummary(
        amount=total_amount,
        payed=total_paid,
        balance=balance,
        sessions=sessions_count,
        average=average,
    )