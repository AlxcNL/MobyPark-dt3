import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database import get_db
from app import models, schemas
from app.dependencies import get_current_user
from app.security import (
    verify_password, hash_password,
    create_token, check_token,
    remove_token, remove_all_tokens_for_user
)

router = APIRouter(prefix="", tags=["auth"])  
bearer_scheme = HTTPBearer(auto_error=True)

@router.put("/businesses", response_model=schemas.Message)
async def update_business(
    payload: schemas.BusinessUpdate,
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_business_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    changed = False
    result = await db.execute(select(models.Business).where(models.Business.id == current_business_user.business_id))
    current_business = result.scalar_one_or_none()
    
    if not current_business:
        raise HTTPException(status_code=404, detail="Business does not exists")
    
    if payload.name is not None:
        current_business.name = payload.name
        changed = True
    if payload.address is not None:
        current_business.address = payload.address
        changed = True
    
    if changed:
        db.add(current_business)
        await db.commit()
    else:
        return schemas.Message(message="No changes provided.")
    
    return schemas.Message(message="Business details have been changed succesfully")
    
@router.post("/businesses", response_model=schemas.Message)
async def register_business(payload: schemas.BusinessCreate, db: AsyncSession = Depends(get_db)):
    #username or email already exists
    result = await db.execute(
    select(models.User).where(
        or_(
            models.User.email == payload.email,
            models.User.username == payload.username,
            )
        )
    )
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    #if business with same name exists
    result = await db.execute(select(models.Business).where(models.Business.name == payload.business_name))
    business = result.scalar_one_or_none()
    if business:
        raise HTTPException(status_code=400, detail="Business name already exists")
    
    new_business = models.Business(
        name=payload.business_name,
        address=payload.address
    )
    db.add(new_business)
    
    await db.commit()
    await db.refresh(new_business)
    
    new_user = models.User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        phone=payload.phone,
        birth_year=payload.birth_year,
        role=payload.role.upper(),
        business_id=new_business.id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)  
    
    result = await db.execute(
        select(models.User).where(
            (models.User.business_id == new_business.id)
            & (models.User.id == new_user.id)
        )
    )
    new_user = result.scalar_one_or_none()
    if not new_user:
        logging.error("Business ID does not exist when adding user or user could not be added")
        raise HTTPException(status_code=404, detail="Something went wrong when adding the business")
    
    return schemas.Message(message="Business registered successfully.")

# parking lots van een business
@router.get("/businesses/{business_id}/parking-lots", response_model=schemas.ParkingLotDetails)
async def get_parking_lot(business_id: int, db: AsyncSession = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    result = await db.execute(select(models.ParkingLot).where(models.ParkingLot.business_id == business_id))
    lot = result.scalar_one_or_none()
    if not lot:
        logging.error("Parking lot not found")
        raise HTTPException(status_code=404, detail="Parking lot not found")
    return lot

@router.get("/businesses/{business_id}", response_model=schemas.BusinessRead)
async def get_business(business_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Business).where(models.Business.id == business_id))
    business = result.scalar_one_or_none()
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    return business

@router.get("/businesses", response_model=list[schemas.BusinessRead])
async def get_all_businesses(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Business))
    businesses = result.scalars().all()
    return businesses