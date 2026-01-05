# app/models.py
from __future__ import annotations

from typing import List, Optional
from datetime import datetime 

from sqlalchemy import (
    String,
    Integer,
    DateTime,
    Text,
    ForeignKey,
    CheckConstraint,
    UniqueConstraint,
    Float,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    full_name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False, default="USER")
    active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    business_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("role in ('USER','ADMIN')", name="ck_users_role"),
    )

    vehicles: Mapped[List["Vehicle"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    payments_initiated: Mapped[List["Payment"]] = relationship(
        back_populates="initiator",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="Payment.initiator_users_id",
    )

class Vehicle(Base):
    __tablename__ = "vehicles"

    vehicle_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    license_plate: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    vehicle_name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    brand: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="vehicles")

    sessions: Mapped[List["Session"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reservations: Mapped[List["Reservation"]] = relationship(
        back_populates="vehicle",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)
    postal_code: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    available_spots: Mapped[int] = mapped_column(Integer, nullable=False)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False)
    daily_rate: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint("total_capacity >= 0", name="ck_parking_lots_capacity"),
        CheckConstraint(
            "available_spots >= 0 AND available_spots <= total_capacity", name="ck_parking_lots_available"
        ),
    )

    sessions: Mapped[List["Session"]] = relationship(
        back_populates="parking_lot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    reservations: Mapped[List["Reservation"]] = relationship(
        back_populates="parking_lot",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    business_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    parking_lots_id: Mapped[int] = mapped_column(
        ForeignKey("parking_lots.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicle_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vehicles.vehicle_id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
        index=True,
    )

    license_plate: Mapped[str] = mapped_column(String, nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    hourly_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    calculated_amount: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes >= 0",
            name="ck_sessions_duration",
        ),
        CheckConstraint(
            "status in ('ACTIVE','COMPLETED','CANCELLED')",
            name="ck_sessions_status",
        ),
    )

    parking_lot: Mapped["ParkingLot"] = relationship(back_populates="sessions")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="sessions")

    payments_session: Mapped[List["Payment"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
        passive_deletes=True,
        foreign_keys="Payment.sessions_id",
    )

class Reservation(Base):
    __tablename__ = "reservation"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    vehicles_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.vehicle_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    parking_lots_id: Mapped[int] = mapped_column(
        ForeignKey("parking_lots.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    start_time: Mapped[str] = mapped_column(String, nullable=False)
    end_time: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="confirmed")
    created_at: Mapped[str] = mapped_column(String, server_default=func.datetime('now'))
    cost: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    __table_args__ = (
        CheckConstraint(
            "status in ('confirmed','completed','canceled')",
            name="ck_reservation_status",
        ),
    )

    parking_lot: Mapped["ParkingLot"] = relationship(back_populates="reservations")
    vehicle: Mapped["Vehicle"] = relationship(back_populates="reservations")

class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)  # cents
    sessions_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    initiator_users_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    method: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    issuer: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    bank: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    initiator: Mapped["User"] = relationship(
        back_populates="payments_initiated", foreign_keys=[initiator_users_id]
    )
    session: Mapped["Session"] = relationship(
        back_populates="payments_session",
        foreign_keys=[sessions_id]
    )
    
class Business(Base):
    __tablename__ = "businesses"
    
    id: Mapped[int] = mapped_column("business_id", primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    address: Mapped[str] = mapped_column(String, nullable=False)