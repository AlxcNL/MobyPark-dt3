import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app import models, schemas
from app.security import check_token ,require_admin
from app.dependencies import get_current_user, page_params, PageParams, calculate_price

from datetime import datetime, timezone
from app.logging_setup import log_event

router = APIRouter(prefix="/parking-lots/{lid}", tags=["sessions"])
bearer_scheme = HTTPBearer(auto_error=True)

# start a session
@router.post("/sessions/start", response_model=schemas.MessageWithId, status_code=201)
async def create_session(
    session: schemas.SessionCreate,
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    parking_lot_result = await db.execute(
        select(models.ParkingLot).where(models.ParkingLot.id == lid)
    )
    parking_lot = parking_lot_result.scalars().first()
    if not parking_lot:
        log_event(logging.WARNING, "/sessions/start", 404, "Parking lot not found")
        raise HTTPException(status_code=404, detail="Parking lot not found")

    vehicle_result = await db.execute(
        select(models.Vehicle).where(models.Vehicle.id == session.vehicles_id)
    )
    vehicle = vehicle_result.scalars().first()
    if not vehicle:
        log_event(logging.WARNING, "/sessions/start", 404, "Vehicle not found")
        raise HTTPException(status_code=404, detail="Vehicle not found")

    new_session = models.Session(
        parking_lots_id=session.parking_lots_id,
        vehicles_id=session.vehicles_id,
        start_date=datetime.now(timezone.utc),
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    log_event(logging.INFO, "/sessions/start", 201, "Session started")
    return {"message": "Session started", "id": new_session.id}


# stop a session
@router.post("/sessions/{session_id}/stop", response_model=schemas.Message)
async def stop_session(
    session_id: int,
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    result = await db.execute(
        select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid,
            models.Session.stop_date.is_(None),
        )
    )
    session = result.scalars().first()
    if not session:
        log_event(logging.WARNING, "/sessions/{session_id}/stop", 404, "Active session not found")
        raise HTTPException(status_code=404, detail="No active session found")

    lot_res = await db.execute(
        select(models.ParkingLot).where(models.ParkingLot.id == lid)
    )
    parking_lot = lot_res.scalars().first()
    if not parking_lot:
        log_event(logging.WARNING, "/sessions/{session_id}/stop", 404, "Parking lot not found")
        raise HTTPException(status_code=404, detail="Parking lot not found")

    session.stop_date = datetime.now(timezone.utc)
    start = session.start_date
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)

    session.duration_minutes = int((session.stop_date - start).total_seconds() // 60)

    price_eur, hours, days = calculate_price(parking_lot, start, session.stop_date)
    session.cost = float(price_eur * 100)

    await db.commit()
    await db.refresh(session)

    log_event(logging.INFO, "/sessions/{session_id}/stop", 200, "Session stopped")
    return {"message": "Session stopped"}


@router.get("/sessions", response_model=List[schemas.Session])
async def get_sessions(
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: PageParams = Depends(page_params),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    if current_user.role == "admin":
        query = (
            select(models.Session)
            .where(models.Session.parking_lots_id == lid)
            .offset(page.offset)
            .limit(page.limit)
        )
    else:
        vehicle_result = await db.execute(
            select(models.Vehicle.id).where(models.Vehicle.users_id == current_user.id)
        )
        vehicle_ids = [v[0] for v in vehicle_result.all()]

        query = (
            select(models.Session)
            .where(
                models.Session.parking_lots_id == lid,
                models.Session.vehicles_id.in_(vehicle_ids),
            )
            .offset(page.offset)
            .limit(page.limit)
        )

    result = await db.execute(query)
    sessions = result.scalars().all()

    log_event(logging.INFO, "/sessions", 200, "Sessions listed")
    return sessions


# get specific session
@router.get("/sessions/{session_id}", response_model=schemas.Session)
async def get_session(
    session_id: int,
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    if current_user.role == "admin":
        query = select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid,
        )
    else:
        vehicle_result = await db.execute(
            select(models.Vehicle.id).where(models.Vehicle.users_id == current_user.id)
        )
        vehicle_ids = [v[0] for v in vehicle_result.all()]

        query = select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid,
            models.Session.vehicles_id.in_(vehicle_ids),
        )

    result = await db.execute(query)
    session = result.scalars().first()

    if not session:
        log_event(logging.WARNING, "/sessions/{session_id}", 404, "Session not found")
        raise HTTPException(status_code=404, detail="Session not found")

    log_event(logging.INFO, "/sessions/{session_id}", 200, "Session retrieved")
    return session


# delete a session (only admin)
@router.delete("/sessions/{session_id}", response_model=schemas.Message)
async def delete_session(
    session_id: int,
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)
    require_admin(current_user)

    result = await db.execute(
        select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid,
        )
    )
    session = result.scalars().first()

    if not session:
        log_event(logging.WARNING, "/sessions/{session_id}", 404, "Session not found")
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()

    log_event(logging.INFO, "/sessions/{session_id}", 200, "Session deleted")
    return {"message": "Session deleted"}
