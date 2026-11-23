from datetime import datetime, date as date_type, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import get_current_user
from backend.config import MAX_BOOKING_DURATION_HOURS, MAX_DAILY_BOOKINGS_PER_STUDENT, SLOT_START_HOUR, SLOT_END_HOUR
from backend.database import get_db
from backend.models import Booking, Resource, User
from backend.schemas import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["Bookings"])


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


@router.post("", response_model=BookingResponse)
@router.post("/", response_model=BookingResponse, include_in_schema=False)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Resource must exist and be active
    resource = db.query(Resource).filter(Resource.id == booking_data.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if not resource.is_active:
        raise HTTPException(status_code=400, detail="Resource is currently inactive")

    # 2. start_time < end_time
    if booking_data.start_time >= booking_data.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    # 3. Duration <= MAX_BOOKING_DURATION_HOURS
    start_dt = datetime.combine(booking_data.booking_date, booking_data.start_time)
    end_dt = datetime.combine(booking_data.booking_date, booking_data.end_time)
    duration_hours = (end_dt - start_dt).total_seconds() / 3600
    if duration_hours > MAX_BOOKING_DURATION_HOURS:
        raise HTTPException(
            status_code=400,
            detail=f"Booking duration cannot exceed {MAX_BOOKING_DURATION_HOURS} hours",
        )

    # 4. Time within allowed slot hours
    if booking_data.start_time.hour < SLOT_START_HOUR or booking_data.end_time.hour > SLOT_END_HOUR:
        raise HTTPException(
            status_code=400,
            detail=f"Bookings must be between {SLOT_START_HOUR}:00 and {SLOT_END_HOUR}:00",
        )

    # 5. DOUBLE-BOOKING CHECK
    overlapping = (
        db.query(Booking)
        .filter(
            Booking.resource_id == booking_data.resource_id,
            Booking.booking_date == booking_data.booking_date,
            Booking.status.in_(["confirmed", "blocked"]),
            Booking.start_time < booking_data.end_time,
            Booking.end_time > booking_data.start_time,
        )
        .first()
    )
    if overlapping:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Time slot conflicts with an existing {overlapping.status} booking "
                   f"({overlapping.start_time.strftime('%H:%M')}-{overlapping.end_time.strftime('%H:%M')})",
        )

    # 6. Daily limit for students
    if current_user.role == "student":
        daily_count = (
            db.query(Booking)
            .filter(
                Booking.user_id == current_user.id,
                Booking.booking_date == booking_data.booking_date,
                Booking.status == "confirmed",
            )
            .count()
        )
        if daily_count >= MAX_DAILY_BOOKINGS_PER_STUDENT:
            raise HTTPException(
                status_code=400,
                detail=f"Daily booking limit reached ({MAX_DAILY_BOOKINGS_PER_STUDENT} bookings per day)",
            )

    # Create booking
    booking = Booking(
        user_id=current_user.id,
        resource_id=booking_data.resource_id,
        booking_date=booking_data.booking_date,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        purpose=booking_data.purpose,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return _booking_to_response(booking, db)


@router.get("/my", response_model=list[BookingResponse])
def get_my_bookings(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    bookings = (
        db.query(Booking)
        .filter(Booking.user_id == current_user.id)
        .order_by(Booking.booking_date.desc(), Booking.start_time)
        .all()
    )
    return [_booking_to_response(b, db) for b in bookings]


@router.delete("/{booking_id}")
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only cancel your own bookings")

    if booking.status != "confirmed":
        raise HTTPException(status_code=400, detail="Only confirmed bookings can be cancelled")

    today = date_type.today()
    if booking.booking_date < today:
        raise HTTPException(status_code=400, detail="Cannot cancel past bookings")

    booking.status = "cancelled"
    db.commit()

    return {"detail": "Booking cancelled successfully"}
