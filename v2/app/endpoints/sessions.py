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

router = APIRouter(prefix="/parking-lots/{lid}", tags=["sessions"])
bearer_scheme = HTTPBearer(auto_error=True)

#start a session
@router.post("/sessions/start", response_model=schemas.MessageWithId)
async def create_session(
    session: schemas.SessionCreate,
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    check_token(token.credentials)

    # Validate parking lot exists
    parking_lot_result = await db.execute(
        select(models.ParkingLot).where(models.ParkingLot.id == lid)
    )
    parking_lot = parking_lot_result.scalars().first()
    if not parking_lot:
        logging.error(f"Parking lot with ID {lid} not found")
        raise HTTPException(status_code=404, detail="Parking lot not found")

    # Validate vehicle exists
    vehicle_result = await db.execute(
        select(models.Vehicle).where(models.Vehicle.id == session.vehicles_id)
    )
    vehicle = vehicle_result.scalars().first()
    if not vehicle:
        logging.error(f"Vehicle with ID {session.vehicles_id} not found")
        raise HTTPException(status_code=404, detail="Vehicle not found")

    new_session = models.Session(
        parking_lots_id=session.parking_lots_id,
        vehicles_id=session.vehicles_id,
        start_date=datetime.now(timezone.utc)
    )

    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    logging.info(f"Session started with ID {new_session.id}")
    return {"message": f"Session started with ID {new_session.id}", "id": new_session.id}

#stop a session
@router.post("/sessions/{session_id}/stop", response_model=schemas.Message)
async def stop_session(
    session_id: int,
    lid: int,  # pass as query param (?lid=1) or make it part of the path
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    check_token(token.credentials)

    # fetch active session
    result = await db.execute(
        select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid,
            models.Session.stop_date.is_(None),
        )
    )
    session = result.scalars().first()
    if not session:
        logging.error(f"No active session found with ID {session_id}")
        raise HTTPException(status_code=404, detail="No active session found")

    # fetch parking lot for tariffs
    lot_res = await db.execute(
        select(models.ParkingLot).where(models.ParkingLot.id == lid)
    )
    parking_lot = lot_res.scalars().first()
    if not parking_lot:
        logging.error(f"Parking lot with ID {lid} not found")
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
    logging.info(f"Session {session_id} stopped")
    return {"message": f"Session {session_id} stopped"}

@router.get("/sessions", response_model=List[schemas.Session])
async def get_sessions(
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    page: PageParams = Depends(page_params),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    check_token(token.credentials)
    
    if current_user.role == "admin":
        query = select(models.Session).where(models.Session.parking_lots_id == lid).offset(page.offset).limit(page.limit)
    else:
        #Get user's vehicle IDs
        vehicle_result = await db.execute(
            select(models.Vehicle.id).where(models.Vehicle.users_id == current_user.id)
        )
        vehicle_ids = [v[0] for v in vehicle_result.all()]
        
        query = select(models.Session).where(
            models.Session.parking_lots_id == lid,
            models.Session.vehicles_id.in_(vehicle_ids)
        ).offset(page.offset).limit(page.limit)
    
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return sessions

#get specific session
@router.get("/sessions/{session_id}", response_model=schemas.Session)
async def get_session(
    session_id: int,
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    check_token(token.credentials)

    if current_user.role == "admin":
        query = select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid
        )
    else:
        #Get user's vehicle IDs
        vehicle_result = await db.execute(
            select(models.Vehicle.id).where(models.Vehicle.users_id == current_user.id)
        )
        vehicle_ids = [v[0] for v in vehicle_result.all()]

        query = select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid,
            models.Session.vehicles_id.in_(vehicle_ids)
        )

    result = await db.execute(query)
    session = result.scalars().first()
    
    if not session:
        logging.error(f"Session with ID {session_id} not found")
        raise HTTPException(status_code=404, detail="Session not found")
    logging.info(f"Session {session_id} retrieved")
    return session

#delete a session (only admin)
@router.delete("/sessions/{session_id}", response_model=schemas.Message)
async def delete_session(
    session_id: int,
    lid: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    check_token(token.credentials)
    require_admin(current_user)

    result = await db.execute(
        select(models.Session).where(
            models.Session.id == session_id,
            models.Session.parking_lots_id == lid
        )
    )
    session = result.scalars().first()
    
    if not session:
        logging.error(f"Session with ID {session_id} not found")
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.delete(session)
    await db.commit()
    logging.info(f"Session {session_id} deleted")
    return {"message": f"Session {session_id} deleted"}
