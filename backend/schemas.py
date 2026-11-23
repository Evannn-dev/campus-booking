from datetime import date, time, datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict, EmailStr


# ── Auth ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"
    roll_number: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    role: str
    roll_number: Optional[str] = None
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Resources ─────────────────────────────────────────────────────────────────

class ResourceCreate(BaseModel):
    name: str
    type: str  # "study_room" or "lab"
    capacity: int
    location: str
    equipment_tags: List[str] = []


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    equipment_tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    type: str
    capacity: int
    location: str
    equipment_tags: str  # JSON string — frontend parses it
    is_active: bool


# ── Bookings ──────────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    resource_id: int
    booking_date: date
    start_time: time
    end_time: time
    purpose: str = ""


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resource_id: int
    booking_date: date
    start_time: time
    end_time: time
    purpose: Optional[str] = None
    status: str
    created_at: datetime
    resource_name: Optional[str] = None
    user_name: Optional[str] = None


class BlockSlotRequest(BaseModel):
    resource_id: int
    booking_date: date
    start_time: time
    end_time: time
    purpose: str = "Maintenance"


# ── Availability ──────────────────────────────────────────────────────────────

class SlotInfo(BaseModel):
    start_time: time
    end_time: time
    status: str  # "available", "confirmed", "blocked"
    booking_id: Optional[int] = None
    user_name: Optional[str] = None
    purpose: Optional[str] = None


class AvailabilityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    resource: ResourceResponse
    date: date
    slots: List[SlotInfo]
