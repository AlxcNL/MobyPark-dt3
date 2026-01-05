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

from app.logging_setup import log_event

router = APIRouter(prefix="", tags=["auth"])  
bearer_scheme = HTTPBearer(auto_error=True)
logger = logging.getLogger(__name__)

@router.post("/register", response_model=schemas.Message)
async def register(payload: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == payload.email))
    user = result.scalar_one_or_none()
    if user:
        log_event(logging.WARNING, "/register", 400, "User registration failed: user already exists")
        raise HTTPException(status_code=400, detail="Email already exists")
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
    log_event(logging.WARNING, "/register", 200, "User registration successfully")
    return schemas.Message(message="User registered successfully.")

@router.post("/login", response_model=schemas.TokenResponse)
async def login(payload: schemas.LoginRequest, db: AsyncSession = Depends(get_db)):
    
    result = await db.execute(select(models.User).where(models.User.username == payload.username))
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(payload.password, user.password_hash):
        log_event(logging.WARNING, "/login", 401, "Login failed: invalid credentials")
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    remove_all_tokens_for_user(user.id)
    token = create_token(user.id)

    log_event(logging.INFO, "/login", 200, "Login succeeded")
    return schemas.TokenResponse(access_token=token)

@router.post("/logout")
async def logout(creds: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = creds.credentials

    try:
        check_token(token)
    except HTTPException:
        log_event(logging.WARNING, "/logout", 401, "Logout failed: invalid token")
        raise

    remove_token(token)

    log_event(logging.INFO, "/logout", 200, "Logout succeeded")
    return schemas.Message(message="Logged out successfully.")

@router.get("/profile", response_model=schemas.User)
async def get_profile(current_user: models.User = Depends(get_current_user)):
    # Als get_current_user faalt, wordt al een 401 gegooid → geen extra log nodig
    log_event(logging.INFO, "/profile", 200, "Profile retrieved successfully")
    return current_user

@router.put("/profile", response_model=schemas.User)
async def update_user(
    payload: schemas.UserUpdate,
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    changed = False
    revoke = False

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
    if getattr(payload, "password", None):
        current_user.password_hash = hash_password(payload.password)
        changed = True
        revoke = True

    if not changed:
        log_event(logging.WARNING, "/profile", 400, "Profile update skipped: no changes provided")
        return schemas.Message(message="No changes provided.")

    db.add(current_user)
    await db.commit()
    if revoke:
        remove_token(creds.credentials)
        log_event(logging.INFO, "/profile", 200, "Password updated, token revoked")
        return schemas.Message(message="Password updated. Please log in again.")

    log_event(logging.INFO, "/profile", 200, "Profile updated successfully")
    return current_user