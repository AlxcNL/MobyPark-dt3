import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app import models, schemas
from app.security import check_token ,require_admin
from app.dependencies import get_current_user, page_params, PageParams

from app.logging_setup import log_event

router = APIRouter(prefix="", tags=["reservations"])
bearer_scheme = HTTPBearer(auto_error=True)

@router.post("/reservations", response_model=schemas.Reservation, status_code=201)
async def create_reservation(
    reservation: schemas.ReservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    result = await db.execute(
        select(models.Vehicle).where(
            models.Vehicle.vehicle_id == reservation.vehicles_id,
            models.Vehicle.user_id == current_user.id,
        )
    )
    vehicle = result.scalar_one_or_none()
    if not vehicle:
        log_event(logging.WARNING, "/reservations", 403, "Reservation creation forbidden: vehicle not owned or not found")
        raise HTTPException(
            status_code=403,
            detail="Vehicle does not exist or does not belong to the user",
        )

    new_reservation = models.Reservation(
        vehicles_id=reservation.vehicles_id,
        parking_lots_id=reservation.parking_lots_id,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        status="confirmed",
        cost=reservation.cost,
    )

    db.add(new_reservation)
    await db.commit()
    await db.refresh(new_reservation)

    log_event(logging.INFO, "/reservations", 201, "Reservation created")
    return new_reservation


@router.get("/reservations", response_model=List[schemas.Reservation])
async def get_reservations(
    db: AsyncSession = Depends(get_db),
    page: PageParams = Depends(page_params),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    query = select(models.Reservation).offset(page.offset).limit(page.limit)
    result = await db.execute(query)
    reservations = result.scalars().all()

    log_event(logging.INFO, "/reservations", 200, "Reservations listed")
    return reservations


@router.get("/reservations/{reservation_id}", response_model=schemas.Reservation)
async def get_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    result = await db.execute(
        select(models.Reservation).where(models.Reservation.id == reservation_id)
    )
    reservation = result.scalar_one_or_none()

    if not reservation:
        log_event(logging.WARNING, "/reservations/{reservation_id}", 404, "Reservation not found")
        raise HTTPException(status_code=404, detail="Reservation not found")

    log_event(logging.INFO, "/reservations/{reservation_id}", 200, "Reservation retrieved")
    return reservation


@router.put("/reservations/{reservation_id}", response_model=schemas.Reservation)
async def update_reservation(
    reservation_id: int,
    reservation_update: schemas.ReservationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    result = await db.execute(
        select(models.Reservation).where(models.Reservation.id == reservation_id)
    )
    reservation = result.scalar_one_or_none()

    if not reservation:
        log_event(logging.WARNING, "/reservations/{reservation_id}", 404, "Reservation not found")
        raise HTTPException(status_code=404, detail="Reservation not found")

    if reservation_update.vehicles_id is not None:
        reservation.vehicles_id = reservation_update.vehicles_id
    if reservation_update.parking_lots_id is not None:
        reservation.parking_lots_id = reservation_update.parking_lots_id
    if reservation_update.end_time is not None:
        reservation.end_time = reservation_update.end_time
    if reservation_update.status is not None:
        reservation.status = reservation_update.status
    if reservation_update.cost is not None:
        reservation.cost = reservation_update.cost

    db.add(reservation)
    await db.commit()
    await db.refresh(reservation)

    log_event(logging.INFO, "/reservations/{reservation_id}", 200, "Reservation updated")
    return reservation


@router.delete("/reservations/{reservation_id}", response_model=schemas.Message)
async def delete_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)
    require_admin(current_user)

    result = await db.execute(
        select(models.Reservation).where(models.Reservation.id == reservation_id)
    )
    reservation = result.scalar_one_or_none()

    if not reservation:
        log_event(logging.WARNING, "/reservations/{reservation_id}", 404, "Reservation not found")
        raise HTTPException(status_code=404, detail="Reservation not found")

    await db.delete(reservation)
    await db.commit()

    log_event(logging.INFO, "/reservations/{reservation_id}", 200, "Reservation deleted")
    return {"message": "Reservation deleted successfully"}
