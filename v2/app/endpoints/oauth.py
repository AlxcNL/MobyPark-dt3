from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app import models, schemas
from app.security import (
    hash_password, verify_password, create_token, remove_all_tokens_for_user
)

router = APIRouter(prefix="", tags=["auth"])  

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
        birth_year=payload.birth_year
    )
    db.add(new_user)
    await db.commit()
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