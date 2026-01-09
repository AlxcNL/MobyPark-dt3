from __future__ import annotations

import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user, check_token, calculate_price, tr_hash, sum_paid_eur
from app.security import require_admin

from app.logging_setup import log_event

router = APIRouter(prefix="", tags=["billing"])
bearer_scheme = HTTPBearer(auto_error=True)

@router.get("/billing", response_model=schemas.BillingSummary)
async def billing_summary_me(
    db: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: models.User = Depends(get_current_user),
):
    check_token(token.credentials)
    # Get all sessions for the current user where the vehicle belongs to the user and status is completed
    q = (
        select(models.Session, models.ParkingLot, models.Vehicle)
        .join(models.Vehicle, models.Session.vehicle_id == models.Vehicle.vehicle_id)
        .join(models.ParkingLot, models.Session.parking_lots_id == models.ParkingLot.id)
        .where(models.Vehicle.user_id == current_user.id and models.Session.status == "completed")
    )
    res = await db.execute(q)
    rows = res.all()

    total_amount = 0.0
    total_paid = 0.0
    sessions_count = 0

    for s, lot, veh in rows:
        amount_eur, _hours, _days = calculate_price(lot, s.start_date, s.end_date)
        thash = tr_hash(s.id, veh.license_plate)
        paid_eur = await sum_paid_eur(db, s.id, thash)

        total_amount += amount_eur
        total_paid += paid_eur
        sessions_count += 1

    total_amount = round(total_amount, 2)
    total_paid = round(total_paid, 2)
    amount_still_to_pay  = round(total_amount - total_paid, 2)
    average = round(total_amount / sessions_count, 2) if sessions_count else 0.0

    log_event(logging.INFO, "/billing", 200, "Billing summary retrieved")

    return schemas.BillingSummary(
        amount=total_amount,
        payed=total_paid,
        amount_still_to_pay=amount_still_to_pay,
        sessions=sessions_count,
        average=average,
    )


@router.get("/billing/monthly")
async def billing_monthly_me(
    db: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: models.User = Depends(get_current_user),
):
    check_token(token.credentials)

    q = (
        select(
            func.strftime("%Y-%m", models.Session.start_date).label("month"),
            func.count(models.Session.id).label("sessions"),
            func.sum(models.Session.calculated_amount).label("total_cost"),
        )
        .join(models.Vehicle, models.Session.vehicle_id == models.Vehicle.vehicle_id)
        .where(models.Vehicle.user_id == current_user.id)
        .group_by("month")
        .order_by("month")
    )

    res = await db.execute(q)

    return [
        {
            "month": month,
            "sessions": sessions,
            "total_cost": round(total_cost or 0, 2),
        }
        for month, sessions, total_cost in res.all()
    ]



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
        .join(models.Vehicle, models.Session.vehicle_id == models.Vehicle.vehicle_id)
        .join(models.ParkingLot, models.Session.parking_lots_id == models.ParkingLot.id)
        .where(models.Vehicle.user_id == uid)
    )
    res = await db.execute(q)
    rows = res.all()

    total_amount = 0.0
    total_paid = 0.0
    sessions_count = 0

    for s, lot, veh in rows:
        amount_eur, _hours, _days = calculate_price(lot, s.start_date, s.end_date)
        thash = tr_hash(s.id, veh.license_plate)
        paid_eur = await sum_paid_eur(db, s.id, thash)

        total_amount += amount_eur
        total_paid += paid_eur
        sessions_count += 1

    total_amount = round(total_amount, 2)
    total_paid = round(total_paid, 2)
    amount_still_to_pay  = round(total_amount - total_paid, 2)
    average = round(total_amount / sessions_count, 2) if sessions_count else 0.0

    log_event(logging.INFO, "/billing/{uid}", 200, "Billing summary retrieved (admin)")

    return schemas.BillingSummary(
        amount=total_amount,
        payed=total_paid,
        amount_still_to_pay=amount_still_to_pay,
        sessions=sessions_count,
        average=average,
    )
