from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.auth import require_admin
from backend.database import get_db
from backend.models import Booking, Resource, User
from backend.schemas import (
    ResourceCreate, ResourceUpdate, ResourceResponse,
    BookingResponse, BlockSlotRequest,
)

router = APIRouter(prefix="/admin", tags=["Admin"])


def _booking_to_response(booking: Booking, db: Session) -> dict:
    resource = db.query(Resource).filter(Resource.id == booking.resource_id).first()
    user = db.query(User).filter(User.id == booking.user_id).first()
    return {
        "id": booking.id,
        "user_id": booking.user_id,
        "resource_id": booking.resource_id,
        "booking_date": booking.booking_date,
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "purpose": booking.purpose,
        "status": booking.status,
        "created_at": booking.created_at,
        "resource_name": resource.name if resource else None,
        "user_name": user.name if user else None,
    }


@router.post("/resources", response_model=ResourceResponse)
def create_resource(
    data: ResourceCreate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import json
    resource = Resource(
        name=data.name,
        type=data.type,
        capacity=data.capacity,
        location=data.location,
        equipment_tags=json.dumps(data.equipment_tags),
        is_active=True,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


@router.put("/resources/{resource_id}", response_model=ResourceResponse)
def update_resource(
    resource_id: int,
    data: ResourceUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    import json
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    if data.name is not None:
        resource.name = data.name
    if data.capacity is not None:
        resource.capacity = data.capacity
    if data.location is not None:
        resource.location = data.location
    if data.equipment_tags is not None:
        resource.equipment_tags = json.dumps(data.equipment_tags)
    if data.is_active is not None:
        resource.is_active = data.is_active

    db.commit()
    db.refresh(resource)
    return resource


@router.patch("/resources/{resource_id}/toggle", response_model=ResourceResponse)
def toggle_resource(
    resource_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    resource.is_active = not resource.is_active
    db.commit()
    db.refresh(resource)
    return resource


@router.get("/bookings", response_model=list[BookingResponse])
def get_all_bookings(
    date: str = None,
    resource_id: int = None,
    status_filter: str = Query(None, alias="status"),
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    query = db.query(Booking)

    if date:
        try:
            booking_date = datetime.strptime(date, "%Y-%m-%d").date()
            query = query.filter(Booking.booking_date == booking_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

    if resource_id:
        query = query.filter(Booking.resource_id == resource_id)

    if status_filter:
        query = query.filter(Booking.status == status_filter)

    bookings = query.order_by(Booking.booking_date.desc(), Booking.start_time).all()
    return [_booking_to_response(b, db) for b in bookings]


@router.post("/block-slot", response_model=BookingResponse)
def block_slot(
    data: BlockSlotRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    resource = db.query(Resource).filter(Resource.id == data.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    # Overlap check
    overlapping = (
        db.query(Booking)
        .filter(
            Booking.resource_id == data.resource_id,
            Booking.booking_date == data.booking_date,
            Booking.status.in_(["confirmed", "blocked"]),
            Booking.start_time < data.end_time,
            Booking.end_time > data.start_time,
        )
        .first()
    )
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time slot conflicts with an existing {overlapping.status} booking "
                   f"({overlapping.start_time.strftime('%H:%M')}-{overlapping.end_time.strftime('%H:%M')})",
        )

    booking = Booking(
        user_id=admin.id,
        resource_id=data.resource_id,
        booking_date=data.booking_date,
        start_time=data.start_time,
        end_time=data.end_time,
        purpose=data.purpose,
        status="blocked",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return _booking_to_response(booking, db)


@router.delete("/bookings/{booking_id}")
def admin_cancel_booking(
    booking_id: int,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "cancelled"
    db.commit()

    return {"detail": "Booking cancelled by admin"}
