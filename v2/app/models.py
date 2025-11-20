# app/models.py
from __future__ import annotations

from typing import List, Optional
from datetime import datetime  # <-- add this

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

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    users_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    license_plate_clean: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    license_plate: Mapped[str] = mapped_column(String, nullable=False)
    make: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
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
    location: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tariff: Mapped[Optional[float]] = mapped_column(String, nullable=True)
    daytariff: Mapped[Optional[float]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    __table_args__ = (
        CheckConstraint("capacity >= 0", name="ck_parking_lots_capacity"),
        CheckConstraint(
            "reserved >= 0 AND reserved <= capacity", name="ck_parking_lots_reserved"
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

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    parking_lots_id: Mapped[int] = mapped_column(
        ForeignKey("parking_lots.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    vehicles_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    stop_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    cost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    payment_status: Mapped[str] = mapped_column(String, nullable=False, default="pending")

    __table_args__ = (
        CheckConstraint(
            "duration_minutes IS NULL OR duration_minutes >= 0",
            name="ck_sessions_duration",
        ),
        CheckConstraint(
            "payment_status in ('pending','completed')",
            name="ck_sessions_payment_status",
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
        ForeignKey("vehicles.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    parking_lots_id: Mapped[int] = mapped_column(
        ForeignKey("parking_lots.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )

    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String, nullable=False, default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    cost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

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