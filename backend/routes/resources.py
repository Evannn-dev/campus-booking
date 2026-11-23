from datetime import datetime, time

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.config import SLOT_START_HOUR, SLOT_END_HOUR
from backend.database import get_db
from backend.models import Resource, Booking, User
from backend.schemas import ResourceResponse, AvailabilityResponse, SlotInfo
from backend.auth import get_current_user

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("", response_model=list[ResourceResponse])
@router.get("/", response_model=list[ResourceResponse], include_in_schema=False)
def list_resources(
    type: str = None,
    min_capacity: int = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
):
    query = db.query(Resource)
    if is_active is not None:
        query = query.filter(Resource.is_active == is_active)
    if type and type != "all":
        query = query.filter(Resource.type == type)
    if min_capacity:
        query = query.filter(Resource.capacity >= min_capacity)
    return query.order_by(Resource.type, Resource.name).all()


@router.get("/{resource_id}", response_model=ResourceResponse)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.get("/{resource_id}/availability")
def get_availability(
    resource_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    try:
        booking_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get all confirmed/blocked bookings for this resource on this date
    bookings = (
        db.query(Booking)
        .filter(
            Booking.resource_id == resource_id,
            Booking.booking_date == booking_date,
            Booking.status.in_(["confirmed", "blocked"]),
        )
        .all()
    )

    # Build slot grid
    slots = []
    for hour in range(SLOT_START_HOUR, SLOT_END_HOUR):
        slot_start = time(hour, 0)
        slot_end = time(hour + 1, 0)

        slot_info = SlotInfo(
            start_time=slot_start,
            end_time=slot_end,
            status="available",
        )

        # Check if any booking overlaps this hour slot
        for b in bookings:
            if b.start_time < slot_end and b.end_time > slot_start:
                user = db.query(User).filter(User.id == b.user_id).first()
                slot_info = SlotInfo(
                    start_time=slot_start,
                    end_time=slot_end,
                    status=b.status,
                    booking_id=b.id,
                    user_name=user.name if user else None,
                    purpose=b.purpose,
                )
                break

        slots.append(slot_info)

    return {
        "resource": ResourceResponse.model_validate(resource),
        "date": date,
        "slots": [s.model_dump() for s in slots],
    }
