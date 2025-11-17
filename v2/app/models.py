from __future__ import annotations

from typing import Optional
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    CheckConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="user")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    birth_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __table_args__ = (
        CheckConstraint("role in ('user','admin')", name="ck_users_role"),
    )

class ParkingLot(Base):
    __tablename__ = "parking_lots"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tariff: Mapped[Optional[float]] = mapped_column(String, nullable=True)
    daytariff: Mapped[Optional[float]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    table_args = (
        CheckConstraint("capacity >= 0", name="ck_parking_lots_capacity"),
        CheckConstraint(
            "reserved >= 0 AND reserved <= capacity", name="ck_parking_lots_reserved"
        ),
    )

class Payment():
    pass