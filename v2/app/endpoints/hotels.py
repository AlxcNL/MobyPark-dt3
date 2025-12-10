from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.database import get_db
from app import models, schemas
from app.security import check_token, require_admin
from app.dependencies import get_current_user, page_params, PageParams
router = APIRouter(prefix="", tags=["hotels"])

bearer_scheme = HTTPBearer(auto_error=True)

@router.post("/hotels", response_model=schemas.Message)
async def create_parking_lot(
    hotel: schemas.Hotel, 
    db: AsyncSession = Depends(get_db), 
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme), 
    current_user: models.User = Depends(get_current_user)
):
    require_admin(current_user)
    
    new_hotel = models.Hotel(
        name=hotel.name
    )
    db.add(new_hotel)
    await db.commit()
    await db.refresh(new_hotel)

    return schemas.Message(message="Hotel created successfully.")

@router.get("/hotels", response_model=List[schemas.Hotel])
async def get_all_parking_lots(db: AsyncSession = Depends(get_db)):
    query = select(models.Hotel)
    result = await db.execute(query)
    hotels = result.scalars().all()
    return hotels