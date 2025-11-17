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

class ParkingLotBase(BaseModel):
    name: str
    location: str
    address: str
    capacity: int = 0
    reserved: int = 0
    tariff: float
    daytariff: float
    latitude: float
    longitude: float


class CreateParkingLot(ParkingLotBase):
    pass

class UpdateParkingLot(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = Field(default=0, ge=0)
    reserved: Optional[int] = Field(default=0, ge=0)
    tariff: Optional[float] = None
    daytariff: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ParkingLot(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ParkingLotDetails(BaseModel):
    id: int
    name: str
    location: Optional[str] = None
    address: Optional[str] = None
    capacity: int
    reserved: int
    tariff: Optional[float] = None
    daytariff: Optional[float] = None
    created_at: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
    license_plate: str
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = Field(default=None, ge=1900)


class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(VehicleBase):
    license_plate: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = Field(default=None, ge=1900)

class Vehicle(BaseModel):
    id: int
    users_id: int
    license_plate: str
    license_plate_clean: str
    make: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    year: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

