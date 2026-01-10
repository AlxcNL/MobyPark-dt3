from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict, conint
from typing import Optional, Literal, Generic, TypeVar, List
from datetime import datetime

T = TypeVar('T')

class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    limit: int
    offset: int

class Message(BaseModel):
    message: str

class MessageWithId(BaseModel):
    message: str
    id: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 1800


Role = Literal["user", "admin", "USER", "ADMIN"]

class UserBase(BaseModel):
    username: str
    email: str
    name: str
    phone: Optional[str] = None
    role: Role = "user"
    birth_year: int


class UserCreate(UserBase):
    password: str = Field(min_length=6)

class BusinessCreate(UserCreate):
    business_name: str
    address: str
    
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
    name: str
    phone: Optional[str] = None
    birth_year: int
    active: int
    created_at: datetime
    business_id: Optional[int]
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
    business_id: Optional[int] = None

class UpdateParkingLot(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = Field(default=None, ge=0)
    reserved: Optional[int] = Field(default=None, ge=0)
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
    business_id: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)

class VehicleBase(BaseModel):
    license_plate: str
    vehicle_name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None


class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(VehicleBase):
    license_plate: Optional[str] = None
    vehicle_name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None

class Vehicle(BaseModel):
    vehicle_id: int
    user_id: int
    license_plate: str
    vehicle_name: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    is_active: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


ReservationStatus = Literal["confirmed", "completed", "canceled"]

class ReservationBase(BaseModel):
    vehicles_id: int
    parking_lots_id: int
    start_time: str
    end_time: Optional[str] = None
    status: ReservationStatus = "confirmed"
    cost: Optional[float] = Field(default=0.0, ge=0)


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    vehicles_id: Optional[int] = Field(default=None, ge=1)
    parking_lots_id: Optional[int] = Field(default=None, ge=1)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    status: Optional[ReservationStatus] = None
    cost: Optional[float] = Field(default=None, ge=0)

class Reservation(BaseModel):
    id: int
    vehicles_id: int
    parking_lots_id: int
    start_time: str
    end_time: Optional[str] = None
    status: ReservationStatus
    created_at: str
    cost: float

    model_config = ConfigDict(from_attributes=True)

SessionStatus = Literal["ACTIVE", "COMPLETED", "CANCELLED"]

class SessionBase(BaseModel):
    parking_lots_id: int
    vehicle_id: Optional[int] = None
    license_plate: str
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=0, ge=0)
    hourly_rate: Optional[float] = Field(default=0.0, ge=0)
    calculated_amount: Optional[float] = Field(default=0.0, ge=0)
    status: SessionStatus = "ACTIVE"

class SessionCreate(BaseModel):
    # license_plate: str
    vehicle_id: int

class SessionUpdate(BaseModel):
    end_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(default=None, ge=0)
    calculated_amount: Optional[float] = Field(default=None, ge=0)
    status: Optional[SessionStatus] = None

class Session(BaseModel):
    id: int
    parking_lots_id: int
    vehicle_id: Optional[int] = None
    license_plate: str
    start_date: datetime
    end_date: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    hourly_rate: float
    calculated_amount: float
    status: SessionStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# ---------------------------
# Payments
# ---------------------------
class PaymentBase(BaseModel):
    sessions_id: int
    method: Optional[str] = None
    issuer: Optional[str] = None
    bank: Optional[str] = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    pass


class Payment(BaseModel):
    id: int
    amount: float
    initiator_users_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    hash: Optional[str] = None
    method: Optional[str] = None
    issuer: Optional[str] = None
    bank: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
    
class BillingSummary(BaseModel):
    amount: float
    payed: float
    amount_still_to_pay: float
    sessions: int
    average: float

class MonthlyBilling(BaseModel):
    year: int
    month: int
    amount: float
    payed: float
    amount_still_to_pay: float
    sessions: int
    average: float
    
class Business(BaseModel):
    id: int
    name: str
    address: str

class BusinessRead(BaseModel):
    name: Optional[str]
    address: Optional[str]
    
class BusinessUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]