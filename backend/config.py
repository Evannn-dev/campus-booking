import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/campus_booking.db")
SECRET_KEY = os.getenv("SECRET_KEY", "campus-booking-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

MAX_BOOKING_DURATION_HOURS = 2
MAX_DAILY_BOOKINGS_PER_STUDENT = 2
SLOT_START_HOUR = 8
SLOT_END_HOUR = 20
