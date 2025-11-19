from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    vehicles: Mapped[list["Vehicle"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    __table_args__ = (
        CheckConstraint("role in ('user','admin')", name="ck_users_role"),
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


class ParkingLot:
    pass


class Payment:
    pass

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

