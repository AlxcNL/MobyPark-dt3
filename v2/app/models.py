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

class ParkingLot():
    pass

class Payment():
    pass