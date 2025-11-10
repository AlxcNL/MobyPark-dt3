from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from datetime import datetime

class Message(BaseModel):
    message: str


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 600


Role = Literal["user", "admin"]

class UserBase(BaseModel):
    username: str
    email: str
    name: str
    phone: Optional[str] = None
    role: Role = "user"
    birth_year: int


class UserCreate(UserBase):
    password: str = Field(min_length=6)


class UserUpdate(BaseModel):
    # update profile fields (not password)
    name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=6)
    phone: Optional[str] = None
    birth_year: Optional[int] = None

class User(BaseModel):
    id: int
    username: str
    email: str
    role: Role
    name: Optional[str] = None
    phone: Optional[str] = None
    birth_year: Optional[int] = None
    active: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VehicleBase(BaseModel):
    pass