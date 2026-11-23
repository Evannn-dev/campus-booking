import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_color):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_color}"/>'))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def create_report():
    doc = Document()

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(0x22, 0x22, 0x22)

    # ── HEADER / TITLE SECTION (Template Header) ──────────────────────────
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r1 = p1.add_run("School of Computer Science and Engineering\n")
    r1.font.size = Pt(16)
    r1.font.bold = True
    r1.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    r2 = p1.add_run("A Report on\n")
    r2.font.size = Pt(13)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

    r3 = p1.add_run("Mini-Project(CA3)\n")
    r3.font.size = Pt(14)
    r3.font.bold = True
    r3.font.color.rgb = RGBColor(0x2B, 0x6C, 0xB0)

    r4 = p1.add_run('Titled “Campus Study-Room & Lab Slot Booking System”\n\n')
    r4.font.size = Pt(15)
    r4.font.bold = True
    r4.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    r5 = p1.add_run("Course Title: Web Technologies\nCourse Code: CSE2258\n")
    r5.font.size = Pt(12)
    r5.font.bold = True
    r5.font.color.rgb = RGBColor(0x2D, 0x37, 0x48)

    # ── PRESIDENCY UNIVERSITY BANNER ─────────────────────────────────────
    banner_p = doc.add_paragraph()
    banner_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    banner_p.paragraph_format.space_before = Pt(12)
    banner_p.paragraph_format.space_after = Pt(4)

    motto_r = banner_p.add_run("GAIN MORE KNOWLEDGE\nREACH GREATER HEIGHTS\n")
    motto_r.font.size = Pt(8.5)
    motto_r.font.bold = True
    motto_r.font.color.rgb = RGBColor(0x4A, 0x55, 0x68)

    univ_r = banner_p.add_run("PRESIDENCY UNIVERSITY\n")
    univ_r.font.size = Pt(18)
    univ_r.font.bold = True
    univ_r.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    sub_r = banner_p.add_run("Private University Estd. in Karnataka State by Act No. 41 of 2013\n")
    sub_r.font.size = Pt(9.5)
    sub_r.font.italic = True
    sub_r.font.color.rgb = RGBColor(0x71, 0x80, 0x96)

    # Divider line
    div_p = doc.add_paragraph()
    div_p.paragraph_format.space_after = Pt(14)
    div_run = div_p.add_run("―" * 55)
    div_run.font.color.rgb = RGBColor(0xCB, 0xD5, 0xE0)
    div_p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Submission Details
    sub_details = doc.add_paragraph()
    sub_details.paragraph_format.space_after = Pt(8)
    sub_date = sub_details.add_run("Date of Submission: 23/11/2026\n")
    sub_date.font.bold = True
    sub_by = sub_details.add_run("Submitted By:\nName: Avanthika P")
    sub_by.font.bold = True

    # ── SUBMITTED BY TABLE ────────────────────────────────────────────────
    table = doc.add_table(rows=6, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    col_widths = [Inches(0.8), Inches(2.6), Inches(1.8), Inches(1.3)]
    headers = ["Sl.No", "Name", "Roll.No", "Sign"]

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1A365D")
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
            run.font.size = Pt(10)

    # Data Rows
    row_data = [
        ("1", "Avanthika P", "20251CSE0264", ""),
        ("2", "", "", ""),
        ("3", "", "", ""),
        ("4", "", "", ""),
        ("5", "", "", ""),
    ]

    for row_idx, data in enumerate(row_data, start=1):
        row_cells = table.rows[row_idx].cells
        for col_idx, text in enumerate(data):
            row_cells[col_idx].text = text
            set_cell_margins(row_cells[col_idx], top=100, bottom=100, left=150, right=150)
            if row_idx % 2 == 1:
                set_cell_background(row_cells[col_idx], "F7FAFC")
            p = row_cells[col_idx].paragraphs[0]
            if col_idx in [0, 2, 3]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.size = Pt(10)
                if row_idx == 1 and col_idx in [0, 1, 2]:
                    run.font.bold = True

    # Adjust widths
    for row in table.rows:
        for idx, width in enumerate(col_widths):
            row.cells[idx].width = width

    # Page Break after front matter
    doc.add_page_break()

    # ── INDEX ─────────────────────────────────────────────────────────────
    h_idx = doc.add_heading(level=1)
    r_idx = h_idx.add_run("Index")
    r_idx.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    idx_table = doc.add_table(rows=6, cols=3)
    idx_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    idx_col_widths = [Inches(1.0), Inches(4.5), Inches(1.0)]

    idx_headers = ["Section", "Topic / Module Title", "Page No."]
    for i, h in enumerate(idx_headers):
        idx_table.rows[0].cells[i].text = h
        set_cell_background(idx_table.rows[0].cells[i], "2B6CB0")
        set_cell_margins(idx_table.rows[0].cells[i], top=100, bottom=100, left=120, right=120)
        p = idx_table.rows[0].cells[i].paragraphs[0]
        if i != 1:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    index_entries = [
        ("1.0", "Abstract", "3"),
        ("2.0", "Introduction", "4"),
        ("3.0", "About Each Page", "6"),
        ("4.0", "Results with Screenshots", "9"),
        ("5.0", "Conclusion", "13"),
    ]

    for r_idx, entry in enumerate(index_entries, start=1):
        row_cells = idx_table.rows[r_idx].cells
        for c_idx, val in enumerate(entry):
            row_cells[c_idx].text = val
            set_cell_margins(row_cells[c_idx], top=80, bottom=80, left=120, right=120)
            if r_idx % 2 == 1:
                set_cell_background(row_cells[c_idx], "F7FAFC")
            p = row_cells[c_idx].paragraphs[0]
            if c_idx in [0, 2]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for run in p.runs:
                run.font.size = Pt(10)

    for row in idx_table.rows:
        for idx, width in enumerate(idx_col_widths):
            row.cells[idx].width = width

    doc.add_page_break()

    # ── 1. ABSTRACT ───────────────────────────────────────────────────────
    h_abs = doc.add_heading(level=1)
    r_abs = h_abs.add_run("1. Abstract")
    r_abs.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    p_abs1 = doc.add_paragraph(
        "In modern collegiate and university environments, shared campus infrastructure such as research laboratories, "
        "collaborative study rooms, and specialized computing facilities experience continuous high demand. Traditional "
        "approaches relying on manual sign-up sheets, shared spreadsheets, or informal email correspondence frequently suffer "
        "from schedule collisions, double-booking conflicts, lack of fair allocation limits, and administrative overhead."
    )
    p_abs1.paragraph_format.line_spacing = 1.15
    p_abs1.paragraph_format.space_after = Pt(8)

    p_abs2 = doc.add_paragraph(
        "The Campus Study-Room & Lab Slot Booking System is a responsive full-stack web application designed and built "
        "specifically to solve university resource allocation challenges. Engineered without heavy frontend frameworks, "
        "the presentation tier utilizes semantic HTML5, custom responsive CSS3 (employing CSS Grid, Flexbox, and CSS Custom Properties), "
        "and modular vanilla JavaScript (ES6+) with JWT-driven authentication. The backend is powered by Python FastAPI and "
        "SQLAlchemy ORM connected to a persisted relational database (SQLite locally with zero-configuration, seamlessly "
        "configurable to PostgreSQL via environment variables)."
    )
    p_abs2.paragraph_format.line_spacing = 1.15
    p_abs2.paragraph_format.space_after = Pt(8)

    p_abs3 = doc.add_paragraph(
        "Key engineering highlights include a server-side Double-Booking Prevention Algorithm that evaluates overlapping time intervals "
        "(new_start < existing_end AND new_end > existing_start) and immediately returns HTTP 409 Conflict with informative error responses, "
        "fair-use student quotas (maximum 2 consecutive hours per booking, 2 active bookings per day), Role-Based Access Control (RBAC) "
        "separating student and admin permissions, an interactive 8:00 AM to 8:00 PM availability grid, and turnkey Docker containerization "
        "with multi-platform CI/CD automation."
    )
    p_abs3.paragraph_format.line_spacing = 1.15

    # ── 2. INTRODUCTION ───────────────────────────────────────────────────
    h_intro = doc.add_heading(level=1)
    r_intro = h_intro.add_run("2. Introduction")
    r_intro.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    doc.add_heading("2.1 Background and Motivation", level=2)
    doc.add_paragraph(
        "Academic institutions host specialized spaces—such as Cloud & DevOps labs, AI/ML GPU workstations, and group discussion rooms—"
        "which students require for capstone projects, lab coursework, and exam preparation. Without an automated, real-time booking platform, "
        "students waste valuable time searching for empty rooms or dealing with simultaneous reservation conflicts. Facilities also suffer "
        "from under-utilization when slots are unofficially claimed without attendance enforcement."
    )

    doc.add_heading("2.2 Project Objectives", level=2)
    bullet_points = [
        ("Zero-Framework Frontend:", "Build an ultra-fast, responsive Single Page Application (SPA) using purely semantic HTML5, modern CSS3, and vanilla JavaScript."),
        ("Strict Double-Booking Prevention:", "Mathematically validate time intervals on the server to prevent any duplicate or overlapping bookings on the same resource."),
        ("Fair-Use Quotas:", "Enforce a maximum booking duration of 2 consecutive hours and a daily cap of 2 active reservations per student."),
        ("Role-Based Access Control (RBAC):", "Differentiate between Students (search, view availability, book, cancel own) and Administrators (add resources, toggle active status, block maintenance slots, inspect all campus reservations)."),
        ("Reliable Automated Seeding & Testing:", "Provide out-of-the-box demo accounts, realistic campus facilities, and 33 automated pytest test cases validating all critical workflows."),
    ]
    for b_title, b_desc in bullet_points:
        p = doc.add_paragraph(style='List Bullet')
        r_b = p.add_run(b_title + " ")
        r_b.bold = True
        p.add_run(b_desc)

    doc.add_heading("2.3 Technical Architecture", level=2)
    doc.add_paragraph(
        "The project follows a clean three-tier architecture:\n"
        "1. Presentation Tier (Frontend): Semantic HTML5, CSS3 Variables, CSS Grid, modular JavaScript using Fetch API and localStorage token management.\n"
        "2. Application Tier (Backend): Python FastAPI ASGI framework providing RESTful API endpoints, Pydantic v2 data serialization, and passlib/python-jose security.\n"
        "3. Data Tier (Database): SQLAlchemy 2.0 ORM with relational schema (users, resources, bookings) persisting to SQLite or PostgreSQL."
    )

    # ── 3. ABOUT EACH PAGE ────────────────────────────────────────────────
    h_pages = doc.add_heading(level=1)
    r_pages = h_pages.add_run("3. About Each Page")
    r_pages.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    doc.add_heading("3.1 Authentication & Registration Page", level=2)
    doc.add_paragraph(
        "The authentication interface serves as the entry point for all campus users. Key capabilities include:\n"
        "• Dual-Tab Layout: Instant toggling between User Login and New Account Registration.\n"
        "• Institutional Roll Number: Registration captures student name, university email, roll number, and password.\n"
        "• One-Click Quick-Fill Buttons: Dedicated quick-fill buttons for 'Demo Admin' (admin@campus.edu) and 'Demo Student' (student1@campus.edu) for rapid testing.\n"
        "• Session Security: On successful authentication, the server returns a signed JWT bearer token stored securely in localStorage, with automatic user session hydration upon page refresh."
    )

    doc.add_heading("3.2 Campus Resource Explorer & Filter Page", level=2)
    doc.add_paragraph(
        "The primary landing dashboard for logged-in students and staff to explore academic facilities:\n"
        "• Filter Bar: Filters facilities by Type (All, Study Rooms, Labs), Minimum Seating Capacity (Any, 5+, 10+, 20+), and Reservation Date.\n"
        "• Resource Cards: Dynamic card components displaying room name, category badges, location info, seating capacity, and equipment tags (e.g., Linux Workstations, Projector, GPU Workstations).\n"
        "• Slot Trigger: Each card includes a 'View Slots' action that fetches real-time slot data from the availability endpoint."
    )

    doc.add_heading("3.3 Interactive Daily Time-Slot Grid & Booking Modal", level=2)
    doc.add_paragraph(
        "The core scheduling component rendering a 12-hour interactive matrix (8:00 AM to 8:00 PM in 1-hour blocks):\n"
        "• Real-Time Visual Coding:\n"
        "   - Green (Available): Open slot, cursor changes to pointer to initiate booking.\n"
        "   - Blue (Your Booking): Highlighted slot currently reserved by the logged-in student.\n"
        "   - Purple/Indigo (Booked): Slot reserved by another campus student.\n"
        "   - Orange (Blocked): Slot blacked out by administrators for maintenance or lab exams.\n"
        "• Interactive Booking Modal: Pre-fills selected resource, date, and start time. Allows selecting 1-hour or 2-hour durations and capturing the academic purpose of the session."
    )

    doc.add_heading("3.4 Student 'My Bookings' Dashboard", level=2)
    doc.add_paragraph(
        "A personal management view allowing students to track their reservation commitments:\n"
        "• Booking Cards / List: Displays resource name, date, formatted 12-hour time range, purpose, and status badges (confirmed, cancelled, blocked).\n"
        "• Cancellation Action: Confirmed upcoming bookings provide an immediate 'Cancel' button that triggers a DELETE request, marking the booking cancelled and freeing the slot for others.\n"
        "• Historical Tracking: Past reservations are preserved in the list for institutional attendance records."
    )

    doc.add_heading("3.5 Administrative Control Panel", level=2)
    doc.add_paragraph(
        "A role-gated administrative interface only visible to users logged in with role='admin':\n"
        "• Add Resource Form: Allows administrators to create new study rooms and labs with custom equipment arrays.\n"
        "• Active/Inactive Toggle: Allows immediate toggling of facility availability (e.g., pulling a room offline for semester repairs).\n"
        "• Maintenance Slot Blocker: Direct tool to block any time interval on any facility with custom reasons (e.g., Midterm Practical Exams, Hardware Servicing).\n"
        "• Campus-Wide Audit Table: Live log of all bookings across campus with user names, dates, times, and administrative cancel overrides."
    )

    # ── 4. RESULTS WITH SCREENSHOTS ────────────────────────────────────────
    h_res = doc.add_heading(level=1)
    r_res = h_res.add_run("4. Results with Screenshots")
    r_res.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    doc.add_paragraph(
        "The application was tested extensively under live server execution at http://localhost:8000 and through an automated "
        "pytest suite containing 33 unit and integration tests. Below are the functional results and UI mockups."
    )

    doc.add_heading("4.1 User Authentication & Quick-Fill View", level=2)
    doc.add_paragraph(
        "The interface loads seamlessly with institutional branding. Clicking 'Demo Student' instantly populates credentials, "
        "and submission generates a cryptographically signed JWT token."
    )
    doc.add_paragraph(
        "[ Screenshot 1: Login & Registration View with Quick-Fill Buttons ]\n"
        "URL: http://localhost:8000\n"
        "Status: 200 OK | Authenticated via POST /api/auth/login"
    )

    doc.add_heading("4.2 Resource Explorer & Dynamic Slot Grid", level=2)
    doc.add_paragraph(
        "Resources are rendered dynamically with capacity and equipment badges. Clicking 'View Slots' dynamically renders the "
        "8:00 AM – 8:00 PM availability grid."
    )
    doc.add_paragraph(
        "[ Screenshot 2: Resource Cards and Interactive 8 AM - 8 PM Slot Grid ]\n"
        "URL: http://localhost:8000 (Resources Tab)\n"
        "Status: 200 OK | Data fetched via GET /api/resources and GET /api/resources/{id}/availability"
    )

    doc.add_heading("4.3 Double-Booking Prevention & Error Toast (HTTP 409)", level=2)
    doc.add_paragraph(
        "When a user attempts to book a slot that overlaps with an existing confirmed reservation or an administrative block, "
        "the backend server immediately rejects the transaction with HTTP 409 Conflict. A red toast notification clearly states the conflicting time window."
    )
    doc.add_paragraph(
        "[ Screenshot 3: Booking Modal & Overlap Conflict Alert (HTTP 409) ]\n"
        "Server Response:\n"
        "HTTP/1.1 409 Conflict\n"
        "{\"detail\": \"Time slot conflicts with an existing confirmed booking (09:00-10:00)\"}"
    )

    doc.add_heading("4.4 Student 'My Bookings' Dashboard", level=2)
    doc.add_paragraph(
        "Students can inspect their scheduled sessions, observe color-coded status badges, and cancel reservations in one click."
    )
    doc.add_paragraph(
        "[ Screenshot 4: My Bookings Management Interface ]\n"
        "Status: Confirmed / Cancelled pills rendered with immediate slot deallocation."
    )

    doc.add_heading("4.5 Admin Panel & Maintenance Blocker", level=2)
    doc.add_paragraph(
        "Administrators can block maintenance windows and review all bookings across the university."
    )
    doc.add_paragraph(
        "[ Screenshot 5: Admin Dashboard with Facility Management and Slot Blocker ]\n"
        "Access: Restricted by require_admin dependency (HTTP 403 Forbidden for students)."
    )

    doc.add_heading("4.6 Automated Pytest Test Suite Results", level=2)
    doc.add_paragraph(
        "All 33 test cases passed with zero failures across Authentication, Resources, Bookings, Admin Controls, and Edge Cases:\n\n"
        "============================= test session starts ==============================\n"
        "platform darwin -- Python 3.9.6, pytest-8.3.3, pluggy-1.6.0\n"
        "rootdir: /Users/evansthannickal/.gemini/antigravity/scratch/campus-booking\n"
        "collected 33 items\n\n"
        "tests/test_api.py::TestAuth::test_register_success PASSED                [  3%]\n"
        "tests/test_api.py::TestAuth::test_register_duplicate_email PASSED        [  6%]\n"
        "tests/test_api.py::TestAuth::test_login_success PASSED                   [  9%]\n"
        "tests/test_api.py::TestAuth::test_login_invalid_password PASSED          [ 12%]\n"
        "tests/test_api.py::TestAuth::test_login_nonexistent_user PASSED          [ 15%]\n"
        "tests/test_api.py::TestAuth::test_get_me PASSED                          [ 18%]\n"
        "tests/test_api.py::TestAuth::test_get_me_no_token PASSED                 [ 21%]\n"
        "tests/test_api.py::TestResources::test_create_resource_as_admin PASSED   [ 24%]\n"
        "tests/test_api.py::TestResources::test_create_resource_as_student_forbidden PASSED [ 27%]\n"
        "tests/test_api.py::TestResources::test_list_resources PASSED             [ 30%]\n"
        "tests/test_api.py::TestResources::test_filter_resources_by_type PASSED   [ 33%]\n"
        "tests/test_api.py::TestResources::test_filter_resources_by_capacity PASSED [ 36%]\n"
        "tests/test_api.py::TestResources::test_get_availability PASSED           [ 39%]\n"
        "tests/test_api.py::TestBookings::test_create_booking_success PASSED      [ 42%]\n"
        "tests/test_api.py::TestBookings::test_double_booking_conflict PASSED     [ 45%]\n"
        "tests/test_api.py::TestBookings::test_overlapping_booking_conflict PASSED [ 48%]\n"
        "tests/test_api.py::TestBookings::test_non_overlapping_booking_ok PASSED  [ 51%]\n"
        "tests/test_api.py::TestBookings::test_max_duration_exceeded PASSED       [ 54%]\n"
        "tests/test_api.py::TestBookings::test_daily_limit_exceeded PASSED        [ 57%]\n"
        "tests/test_api.py::TestBookings::test_cancel_booking PASSED              [ 60%]\n"
        "tests/test_api.py::TestBookings::test_cannot_cancel_others_booking PASSED [ 63%]\n"
        "tests/test_api.py::TestBookings::test_get_my_bookings PASSED             [ 66%]\n"
        "tests/test_api.py::TestAdmin::test_admin_block_slot PASSED               [ 69%]\n"
        "tests/test_api.py::TestAdmin::test_student_cannot_book_blocked_slot PASSED [ 72%]\n"
        "tests/test_api.py::TestAdmin::test_admin_view_all_bookings PASSED        [ 75%]\n"
        "tests/test_api.py::TestAdmin::test_admin_cancel_any_booking PASSED       [ 78%]\n"
        "tests/test_api.py::TestAdmin::test_toggle_resource PASSED                [ 81%]\n"
        "tests/test_api.py::TestAdmin::test_student_cannot_block_slot PASSED      [ 84%]\n"
        "tests/test_api.py::TestEdgeCases::test_booking_inactive_resource PASSED  [ 87%]\n"
        "tests/test_api.py::TestEdgeCases::test_booking_start_after_end PASSED    [ 90%]\n"
        "tests/test_api.py::TestEdgeCases::test_booking_outside_hours PASSED      [ 93%]\n"
        "tests/test_api.py::TestEdgeCases::test_cancel_already_cancelled PASSED   [ 96%]\n"
        "tests/test_api.py::TestEdgeCases::test_cancelled_slot_becomes_available PASSED [100%]\n\n"
        "============================== 33 passed in 19.45s =============================="
    )

    # ── 5. CONCLUSION ─────────────────────────────────────────────────────
    h_concl = doc.add_heading(level=1)
    r_concl = h_concl.add_run("5. Conclusion")
    r_concl.font.color.rgb = RGBColor(0x1A, 0x36, 0x5D)

    doc.add_heading("5.1 Project Summary", level=2)
    doc.add_paragraph(
        "The Campus Study-Room & Lab Slot Booking System delivers a robust, elegant, and secure digital platform for campus "
        "infrastructure scheduling. By leveraging vanilla web technologies (HTML5, responsive CSS3, ES6+ JavaScript) combined "
        "with Python FastAPI and SQLAlchemy ORM, the application avoids unnecessary dependencies while maintaining high performance, "
        "airtight double-booking protection, and strict role-based access control. The interactive slot grid delivers a transparent, "
        "user-friendly experience that eliminates manual reservation friction."
    )

    doc.add_heading("5.2 Future Scope & Enhancements", level=2)
    future_points = [
        ("QR-Code Entry Validation:", "Install physical tablet or barcode scanners at room entrances to verify student attendance within 15 minutes of slot start."),
        ("Automated Alerts & Reminders:", "Send automated email or SMS notifications 30 minutes before a booked slot."),
        ("Calendar Synchronization:", "Enable one-click .ics download or Google Calendar integration for scheduled slots."),
        ("Semester-Long Recurring Bookings:", "Enable faculty members to reserve laboratory slots on recurring weekly schedules for practical classes."),
    ]
    for f_title, f_desc in future_points:
        p = doc.add_paragraph(style='List Bullet')
        r_f = p.add_run(f_title + " ")
        r_f.bold = True
        p.add_run(f_desc)

    # Signature Footer
    doc.add_paragraph()
    sig_p = doc.add_paragraph()
    sig_p.paragraph_format.space_before = Pt(20)
    sig_p.add_run("Submitted for Evaluation by:\n").bold = True
    sig_p.add_run("Candidate Name: Avanthika P\nRoll Number: 20251CSE0264\nSchool of Computer Science and Engineering\nPresidency University")

    # Output paths
    output_dir = "/Users/evansthannickal/.gemini/antigravity/scratch/campus-booking/frontend"
    output_path = os.path.join(output_dir, "Campus_Booking_Report_Avanthika_P.docx")
    doc.save(output_path)
    print(f"Report successfully saved to: {output_path}")

    # Also save to current project root
    root_path = "/Users/evansthannickal/.gemini/antigravity/scratch/campus-booking/Campus_Booking_Report_Avanthika_P.docx"
    doc.save(root_path)
    print(f"Report also saved to root: {root_path}")

if __name__ == "__main__":
    create_report()
