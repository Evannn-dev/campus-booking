import json
from datetime import date, time, timedelta

from sqlalchemy.orm import Session

from backend.auth import hash_password
from backend.models import User, Resource, Booking


def seed_database(db: Session):
    """Seed the database with demo data if it's empty."""
    if db.query(User).count() > 0:
        return

    print("🌱 Seeding database with demo data...")

    # ── Users ─────────────────────────────────────────────────────────────
    admin = User(
        name="Campus Admin",
        email="admin@campus.edu",
        password_hash=hash_password("admin123"),
        role="admin",
    )
    student1 = User(
        name="Alice Johnson",
        email="student1@campus.edu",
        password_hash=hash_password("student123"),
        role="student",
        roll_number="CS2024001",
    )
    student2 = User(
        name="Bob Smith",
        email="student2@campus.edu",
        password_hash=hash_password("student123"),
        role="student",
        roll_number="EC2024002",
    )
    db.add_all([admin, student1, student2])
    db.flush()

    # ── Resources ─────────────────────────────────────────────────────────
    resources_data = [
        {
            "name": "Library Discussion Room A",
            "type": "study_room",
            "capacity": 6,
            "location": "Central Library 2nd Floor",
            "equipment_tags": ["Whiteboard", "Power Outlets"],
        },
        {
            "name": "Library Discussion Room B",
            "type": "study_room",
            "capacity": 10,
            "location": "Central Library 3rd Floor",
            "equipment_tags": ["Whiteboard", "Projector", "Power Outlets"],
        },
        {
            "name": "Quiet Study Hall",
            "type": "study_room",
            "capacity": 30,
            "location": "Main Building Ground Floor",
            "equipment_tags": ["Individual Desks", "Power Outlets", "Wi-Fi"],
        },
        {
            "name": "DevOps & Cloud Lab",
            "type": "lab",
            "capacity": 25,
            "location": "CS Building Room 201",
            "equipment_tags": ["Linux Workstations", "Docker", "Kubernetes Cluster"],
        },
        {
            "name": "AI/ML Research Lab",
            "type": "lab",
            "capacity": 20,
            "location": "CS Building Room 305",
            "equipment_tags": ["GPU Workstations", "NVIDIA A100", "JupyterHub"],
        },
        {
            "name": "Electronics & IoT Lab",
            "type": "lab",
            "capacity": 15,
            "location": "ECE Building Room 102",
            "equipment_tags": ["Oscilloscopes", "Arduino Kits", "Soldering Stations"],
        },
    ]

    resource_objs = []
    for r in resources_data:
        resource = Resource(
            name=r["name"],
            type=r["type"],
            capacity=r["capacity"],
            location=r["location"],
            equipment_tags=json.dumps(r["equipment_tags"]),
        )
        db.add(resource)
        resource_objs.append(resource)
    db.flush()

    # ── Sample Bookings ───────────────────────────────────────────────────
    today = date.today()
    tomorrow = today + timedelta(days=1)

    sample_bookings = [
        # Alice books Discussion Room A today 9-10 AM
        Booking(
            user_id=student1.id,
            resource_id=resource_objs[0].id,
            booking_date=today,
            start_time=time(9, 0),
            end_time=time(10, 0),
            purpose="Group project meeting",
            status="confirmed",
        ),
        # Alice books AI/ML Lab today 14-16
        Booking(
            user_id=student1.id,
            resource_id=resource_objs[4].id,
            booking_date=today,
            start_time=time(14, 0),
            end_time=time(16, 0),
            purpose="Deep learning assignment",
            status="confirmed",
        ),
        # Bob books DevOps Lab today 10-12
        Booking(
            user_id=student2.id,
            resource_id=resource_objs[3].id,
            booking_date=today,
            start_time=time(10, 0),
            end_time=time(12, 0),
            purpose="Kubernetes lab exercise",
            status="confirmed",
        ),
        # Bob books Discussion Room B tomorrow 11-12
        Booking(
            user_id=student2.id,
            resource_id=resource_objs[1].id,
            booking_date=tomorrow,
            start_time=time(11, 0),
            end_time=time(12, 0),
            purpose="Presentation rehearsal",
            status="confirmed",
        ),
        # Admin blocks Electronics Lab tomorrow 8-10 for maintenance
        Booking(
            user_id=admin.id,
            resource_id=resource_objs[5].id,
            booking_date=tomorrow,
            start_time=time(8, 0),
            end_time=time(10, 0),
            purpose="Equipment maintenance",
            status="blocked",
        ),
    ]

    db.add_all(sample_bookings)
    db.commit()

    print("✅ Database seeded with 3 users, 6 resources, and 5 sample bookings")
