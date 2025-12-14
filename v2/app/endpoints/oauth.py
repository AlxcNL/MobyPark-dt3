import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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

@router.post("/register", response_model=schemas.Message)
async def register(payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == payload.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = models.User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        phone=payload.phone,
        birth_year=payload.birth_year,
        role=payload.role
    )
    db.add(new_user)
    await db.commit()
    logging.info(f"User registered: {payload.username}")
    return schemas.Message(message="User registered successfully.")

@router.post("/login", response_model=schemas.TokenResponse)
async def login(payload: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(models.User).where(models.User.username == payload.username))
    user = result.scalar_one_or_none()
    print(user)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    remove_all_tokens_for_user(user.id)
    token = create_token(user.id)
    return schemas.TokenResponse(access_token=token)

@router.post("/logout")
async def logout(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = creds.credentials
    check_token(token)
    remove_token(token)
    return schemas.Message(message="Logged out successfully.")

@router.get("/profile", response_model=schemas.User)
async def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.put("/profile", response_model=schemas.Message)
async def update_user(
    payload: schemas.UserUpdate,
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    changed = False
    # safe profile fields
    if payload.name is not None:
        current_user.name = payload.name
        changed = True
    if payload.phone is not None:
        current_user.phone = payload.phone
        changed = True
    if payload.birth_year is not None:
        current_user.birth_year = payload.birth_year
        changed = True

    # optional password change
    new_pw = getattr(payload, "password", None)
    if new_pw:
        current_user.password_hash = hash_password(new_pw)
        changed = True
        revoke = True
    else:
        revoke = False

    if changed:
        db.add(current_user)
        await db.commit()
    else:
        return schemas.Message(message="No changes provided.")

    if revoke:
        token = creds.credentials
        remove_token(token)
        return schemas.Message(message="Password updated. Please log in again.")

    return schemas.Message(message="Profile updated successfully.")

@router.post("/register/hotel", response_model=schemas.Message)
async def register(payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == payload.email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_hotel = models.Hotel(
        name=payload.name
    )
    db.add(new_hotel)
    await db.commit()
    await db.refresh(new_hotel)
    new_user = models.User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        name=payload.name,
        phone=payload.phone,
        birth_year=payload.birth_year,
        role=payload.role,
        hotel_id=new_hotel.hotel_id
    )
    db.add(new_user)
    await db.commit()
    return schemas.Message(message="Hotel registered successfully.")