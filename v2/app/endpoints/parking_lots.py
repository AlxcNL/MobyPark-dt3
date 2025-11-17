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

@router.get("/parking-lots", response_model=schemas.Page[schemas.ParkingLot])
async def list_parking_lots(p: PageParams = Depends(page_params), db: AsyncSession = Depends(get_db), creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    check_token(creds.credentials)

    # total count
    total = (await db.execute(select(func.count()).select_from(models.ParkingLot))).scalar_one()

    # page of rows
    result = await db.execute(
        select(models.ParkingLot)
        .order_by(models.ParkingLot.id)
        .offset(p.offset)
        .limit(p.limit)
    )
    rows = result.scalars().all()

    # thanks to from_attributes=True you can return ORM rows
    items = rows
    return schemas.Page(items=items, total=total, limit=p.limit, offset=p.offset)
