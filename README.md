# 🏛️ Campus Study-Room & Lab Slot Booking System

A full-stack web application for booking study rooms and labs across a university campus, with real-time availability grids, role-based access control, and double-booking prevention.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- **🔐 JWT Authentication** — Register and login with role-based access (Student / Admin)
- **📅 Interactive Slot Grid** — Visual 8 AM–8 PM time grid showing availability in real-time
- **🛡️ Double-Booking Prevention** — Server-side overlap detection returning HTTP 409 Conflict
- **📊 Student Booking Rules** — Max 2-hour duration, max 2 bookings per day per student
- **🔒 Admin Controls** — Create/edit resources, block maintenance slots, view all bookings
- **🎨 Responsive UI** — Clean HTML/CSS/JS frontend with cards, grids, and toast notifications
- **🐳 Docker Ready** — Single-command deployment with docker-compose
- **🧪 Tested** — pytest suite covering auth, conflicts, limits, and admin operations

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3 (Grid/Flexbox), Vanilla JavaScript |
| Backend | Python FastAPI, SQLAlchemy ORM, Pydantic |
| Database | SQLite (default) / PostgreSQL (via env var) |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| CI/CD | GitHub Actions, Docker multi-platform builds |

## 🚀 Quick Start

### Local Development

```bash
# Clone and enter the project
cd campus-booking

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn backend.main:app --reload --port 8000
```

Open http://localhost:8000 in your browser.

### Docker

```bash
docker-compose up --build
```

The app is available at http://localhost:8000.

## 🔑 Default Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@campus.edu` | `admin123` |
| Student 1 | `student1@campus.edu` | `student123` |
| Student 2 | `student2@campus.edu` | `student123` |

## 📡 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login, get JWT |
| GET | `/api/auth/me` | Current user info |

### Resources
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/resources` | List resources (filter by type, capacity) |
| GET | `/api/resources/{id}` | Get resource details |
| GET | `/api/resources/{id}/availability?date=YYYY-MM-DD` | Slot availability grid |

### Bookings (Student)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/bookings` | Create booking |
| GET | `/api/bookings/my` | My bookings |
| DELETE | `/api/bookings/{id}` | Cancel booking |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/resources` | Create resource |
| PUT | `/api/admin/resources/{id}` | Update resource |
| PATCH | `/api/admin/resources/{id}/toggle` | Toggle active status |
| GET | `/api/admin/bookings` | All bookings |
| POST | `/api/admin/block-slot` | Block maintenance slot |
| DELETE | `/api/admin/bookings/{id}` | Cancel any booking |

## 📂 Project Structure

```
campus-booking/
├── backend/
│   ├── __init__.py
│   ├── config.py          # Environment config
│   ├── database.py        # SQLAlchemy engine & session
│   ├── models.py          # ORM models (User, Resource, Booking)
│   ├── schemas.py         # Pydantic validation models
│   ├── auth.py            # JWT + bcrypt utilities
│   ├── seed.py            # Demo data seeder
│   ├── main.py            # FastAPI app entrypoint
│   └── routes/
│       ├── auth_routes.py
│       ├── resources.py
│       ├── bookings.py
│       └── admin.py
├── frontend/
│   ├── index.html
│   ├── css/styles.css
│   └── js/
│       ├── api.js         # Fetch wrapper + API methods
│       └── app.js         # SPA logic, DOM rendering
├── tests/
│   ├── conftest.py        # Fixtures, test client
│   └── test_api.py        # 20+ integration tests
├── data/                  # SQLite database (auto-created)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .github/workflows/ci.yml
└── README.md
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📋 Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/campus_booking.db` | Database connection string |
| `SECRET_KEY` | (built-in dev key) | JWT signing secret |

To use PostgreSQL:
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/campus_booking"
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
