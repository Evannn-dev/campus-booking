import json
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, Time, DateTime,
    ForeignKey, Text
)
from sqlalchemy.orm import relationship

from backend.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="student", nullable=False)
    roll_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    bookings = relationship("Booking", back_populates="user")


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(20), nullable=False)  # "study_room" or "lab"
    capacity = Column(Integer, nullable=False)
    location = Column(String(200), nullable=False)
    equipment_tags = Column(Text, default="[]")  # JSON string list
    is_active = Column(Boolean, default=True)

    bookings = relationship("Booking", back_populates="resource")

    def get_equipment_list(self):
        try:
            return json.loads(self.equipment_tags or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def set_equipment_list(self, tags):
        self.equipment_tags = json.dumps(tags)


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    resource_id = Column(Integer, ForeignKey("resources.id"), nullable=False)
    booking_date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    purpose = Column(String(500), nullable=True)
    status = Column(String(20), default="confirmed", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="bookings")
    resource = relationship("Resource", back_populates="bookings")
