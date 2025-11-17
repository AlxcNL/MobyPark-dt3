from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, funct
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app import models, schemas
from app.security import check_token ,require_admin
from app.dependancies import get_current_user, page_params, PageParams

router = APIRouter(prefix="", tags=["parking_lots"])
bearer_scheme = HTTPBearer(auto_error=True)

@router.post("/parking-lots", response_model=schemas.Message)
async def create_parking_lot(lot: schemas.CreateParkingLot, db: AsyncSession = Depends(get_db), creds: HTTPAuthorizationCredentials = Depends(bearer_scheme), current_user: models.User = Depends(get_current_user)):
    require_admin(current_user)

    new_lot = models.ParkingLot(
        name=lot.name,
        location=lot.location,
        address=lot.address,
        capacity=lot.capacity,
        reserved=lot.reserved,
        tariff=lot.tariff,
        daytariff=lot.daytariff,
        latitude=lot.latitude,
        longitude=lot.longitude
    )
    db.add(new_lot)
    await db.commit()
    await db.refresh(new_lot)

    return schemas.Message(message="Parking lot created successfully.")
