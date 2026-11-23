"""
Comprehensive test suite for the Campus Study-Room & Lab Slot Booking System.
Tests cover JWT auth, RBAC, double-booking prevention, daily limits,
maintenance blocks, and admin operations.
"""

from datetime import date, time, timedelta

import pytest

# Use tomorrow so bookings are always "future" and cancellable
TOMORROW = (date.today() + timedelta(days=1)).isoformat()
DAY_AFTER = (date.today() + timedelta(days=2)).isoformat()


# ══════════════════════════════════════════════════════════════════════════════
# AUTH TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestAuth:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "name": "New User",
            "email": "new@test.edu",
            "password": "password123",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "name": "User A",
            "email": "dup@test.edu",
            "password": "pass",
        })
        resp = client.post("/api/auth/register", json={
            "name": "User B",
            "email": "dup@test.edu",
            "password": "pass",
        })
        assert resp.status_code == 409

    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "name": "Login User",
            "email": "login@test.edu",
            "password": "mypassword",
        })
        resp = client.post("/api/auth/login", json={
            "email": "login@test.edu",
            "password": "mypassword",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_invalid_password(self, client):
        client.post("/api/auth/register", json={
            "name": "Bad Login",
            "email": "bad@test.edu",
            "password": "correct",
        })
        resp = client.post("/api/auth/login", json={
            "email": "bad@test.edu",
            "password": "wrong",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "ghost@test.edu",
            "password": "whatever",
        })
        assert resp.status_code == 401

    def test_get_me(self, client, student_headers):
        resp = client.get("/api/auth/me", headers=student_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "student@test.edu"
        assert data["role"] == "student"
        assert data["name"] == "Student One"

    def test_get_me_no_token(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
# RESOURCE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestResources:
    def test_create_resource_as_admin(self, client, admin_headers):
        resp = client.post("/api/admin/resources", json={
            "name": "New Room",
            "type": "study_room",
            "capacity": 8,
            "location": "Library",
            "equipment_tags": ["Whiteboard"],
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["name"] == "New Room"

    def test_create_resource_as_student_forbidden(self, client, student_headers):
        resp = client.post("/api/admin/resources", json={
            "name": "Forbidden Room",
            "type": "study_room",
            "capacity": 5,
            "location": "X",
            "equipment_tags": [],
        }, headers=student_headers)
        assert resp.status_code == 403

    def test_list_resources(self, client, sample_resource, sample_lab):
        resp = client.get("/api/resources")
        assert resp.status_code == 200
        resources = resp.json()
        assert len(resources) == 2

    def test_filter_resources_by_type(self, client, sample_resource, sample_lab):
        resp = client.get("/api/resources?type=lab")
        assert resp.status_code == 200
        resources = resp.json()
        assert len(resources) == 1
        assert resources[0]["type"] == "lab"

    def test_filter_resources_by_capacity(self, client, sample_resource, sample_lab):
        resp = client.get("/api/resources?min_capacity=20")
        assert resp.status_code == 200
        resources = resp.json()
        assert len(resources) == 1
        assert resources[0]["capacity"] >= 20

    def test_get_availability(self, client, sample_resource):
        resp = client.get(f"/api/resources/{sample_resource['id']}/availability?date={TOMORROW}")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["slots"]) == 12  # 8 AM to 8 PM = 12 hours
        assert all(s["status"] == "available" for s in data["slots"])


# ══════════════════════════════════════════════════════════════════════════════
# BOOKING TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestBookings:
    def test_create_booking_success(self, client, student_headers, sample_resource):
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Study session",
        }, headers=student_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "confirmed"
        assert data["resource_name"] == "Test Study Room"

    def test_double_booking_conflict(self, client, student_headers, student2_headers, sample_resource):
        # First booking
        client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "First",
        }, headers=student_headers)
        # Same slot, different student
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Second",
        }, headers=student2_headers)
        assert resp.status_code == 409

    def test_overlapping_booking_conflict(self, client, student_headers, student2_headers, sample_resource):
        # Book 9-11
        client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "11:00:00",
            "purpose": "First",
        }, headers=student_headers)
        # Try booking 10-12 (overlaps)
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "10:00:00",
            "end_time": "12:00:00",
            "purpose": "Overlap",
        }, headers=student2_headers)
        assert resp.status_code == 409

    def test_non_overlapping_booking_ok(self, client, student_headers, student2_headers, sample_resource):
        # Book 9-10
        client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "First",
        }, headers=student_headers)
        # Book 10-11 (adjacent, no overlap)
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "10:00:00",
            "end_time": "11:00:00",
            "purpose": "Second",
        }, headers=student2_headers)
        assert resp.status_code == 200

    def test_max_duration_exceeded(self, client, student_headers, sample_resource):
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "purpose": "Too long",
        }, headers=student_headers)
        assert resp.status_code == 400
        assert "duration" in resp.json()["detail"].lower() or "exceed" in resp.json()["detail"].lower()

    def test_daily_limit_exceeded(self, client, student_headers, sample_resource, sample_lab):
        # Booking 1
        client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "First",
        }, headers=student_headers)
        # Booking 2
        client.post("/api/bookings", json={
            "resource_id": sample_lab["id"],
            "booking_date": TOMORROW,
            "start_time": "11:00:00",
            "end_time": "12:00:00",
            "purpose": "Second",
        }, headers=student_headers)
        # Booking 3 — should be rejected (daily limit = 2)
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "14:00:00",
            "end_time": "15:00:00",
            "purpose": "Third",
        }, headers=student_headers)
        assert resp.status_code == 400
        assert "limit" in resp.json()["detail"].lower()

    def test_cancel_booking(self, client, student_headers, sample_resource):
        # Create
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Will cancel",
        }, headers=student_headers)
        booking_id = resp.json()["id"]
        # Cancel
        resp = client.delete(f"/api/bookings/{booking_id}", headers=student_headers)
        assert resp.status_code == 200
        # Verify it's cancelled
        bookings = client.get("/api/bookings/my", headers=student_headers).json()
        cancelled = [b for b in bookings if b["id"] == booking_id]
        assert cancelled[0]["status"] == "cancelled"

    def test_cannot_cancel_others_booking(self, client, student_headers, student2_headers, sample_resource):
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Student 1's",
        }, headers=student_headers)
        booking_id = resp.json()["id"]
        # Student 2 tries to cancel Student 1's booking
        resp = client.delete(f"/api/bookings/{booking_id}", headers=student2_headers)
        assert resp.status_code == 403

    def test_get_my_bookings(self, client, student_headers, sample_resource):
        client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "My booking",
        }, headers=student_headers)
        resp = client.get("/api/bookings/my", headers=student_headers)
        assert resp.status_code == 200
        bookings = resp.json()
        assert len(bookings) == 1
        assert bookings[0]["purpose"] == "My booking"


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestAdmin:
    def test_admin_block_slot(self, client, admin_headers, sample_resource):
        resp = client.post("/api/admin/block-slot", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "08:00:00",
            "end_time": "10:00:00",
            "purpose": "Lab Exam",
        }, headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["status"] == "blocked"

    def test_student_cannot_book_blocked_slot(self, client, admin_headers, student_headers, sample_resource):
        # Admin blocks 8-10
        client.post("/api/admin/block-slot", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "08:00:00",
            "end_time": "10:00:00",
            "purpose": "Maintenance",
        }, headers=admin_headers)
        # Student tries to book 9-10 (overlaps with block)
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Study",
        }, headers=student_headers)
        assert resp.status_code == 409

    def test_admin_view_all_bookings(self, client, admin_headers, student_headers, sample_resource):
        # Student makes a booking
        client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "14:00:00",
            "end_time": "15:00:00",
            "purpose": "Student booking",
        }, headers=student_headers)
        # Admin sees it
        resp = client.get("/api/admin/bookings", headers=admin_headers)
        assert resp.status_code == 200
        bookings = resp.json()
        assert len(bookings) >= 1
        assert any(b["purpose"] == "Student booking" for b in bookings)

    def test_admin_cancel_any_booking(self, client, admin_headers, student_headers, sample_resource):
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "14:00:00",
            "end_time": "15:00:00",
            "purpose": "Will be admin-cancelled",
        }, headers=student_headers)
        booking_id = resp.json()["id"]
        # Admin cancels it
        resp = client.delete(f"/api/admin/bookings/{booking_id}", headers=admin_headers)
        assert resp.status_code == 200

    def test_toggle_resource(self, client, admin_headers, sample_resource):
        rid = sample_resource["id"]
        # Deactivate
        resp = client.patch(f"/api/admin/resources/{rid}/toggle", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is False
        # Reactivate
        resp = client.patch(f"/api/admin/resources/{rid}/toggle", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["is_active"] is True

    def test_student_cannot_block_slot(self, client, student_headers, sample_resource):
        resp = client.post("/api/admin/block-slot", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "08:00:00",
            "end_time": "10:00:00",
            "purpose": "Student tries to block",
        }, headers=student_headers)
        assert resp.status_code == 403


# ══════════════════════════════════════════════════════════════════════════════
# EDGE CASE TESTS
# ══════════════════════════════════════════════════════════════════════════════

class TestEdgeCases:
    def test_booking_inactive_resource(self, client, admin_headers, student_headers, sample_resource):
        rid = sample_resource["id"]
        # Deactivate
        client.patch(f"/api/admin/resources/{rid}/toggle", headers=admin_headers)
        # Try to book
        resp = client.post("/api/bookings", json={
            "resource_id": rid,
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Inactive resource",
        }, headers=student_headers)
        assert resp.status_code == 400
        assert "inactive" in resp.json()["detail"].lower()

    def test_booking_start_after_end(self, client, student_headers, sample_resource):
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "12:00:00",
            "end_time": "10:00:00",
            "purpose": "Invalid times",
        }, headers=student_headers)
        assert resp.status_code == 400

    def test_booking_outside_hours(self, client, student_headers, sample_resource):
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "06:00:00",
            "end_time": "07:00:00",
            "purpose": "Too early",
        }, headers=student_headers)
        assert resp.status_code == 400

    def test_cancel_already_cancelled(self, client, student_headers, sample_resource):
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Cancel twice",
        }, headers=student_headers)
        bid = resp.json()["id"]
        client.delete(f"/api/bookings/{bid}", headers=student_headers)
        # Try again
        resp = client.delete(f"/api/bookings/{bid}", headers=student_headers)
        assert resp.status_code == 400

    def test_cancelled_slot_becomes_available(self, client, student_headers, student2_headers, sample_resource):
        # Student 1 books 9-10
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Will free up",
        }, headers=student_headers)
        bid = resp.json()["id"]
        # Student 1 cancels
        client.delete(f"/api/bookings/{bid}", headers=student_headers)
        # Student 2 can now book the same slot
        resp = client.post("/api/bookings", json={
            "resource_id": sample_resource["id"],
            "booking_date": TOMORROW,
            "start_time": "09:00:00",
            "end_time": "10:00:00",
            "purpose": "Rebooked",
        }, headers=student2_headers)
        assert resp.status_code == 200
