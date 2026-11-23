import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import Base, get_db
from backend.main import app

# In-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def admin_token(client):
    client.post("/api/auth/register", json={
        "name": "Admin User",
        "email": "admin@test.edu",
        "password": "admin123",
        "role": "admin",
    })
    resp = client.post("/api/auth/login", json={
        "email": "admin@test.edu",
        "password": "admin123",
    })
    return resp.json()["access_token"]


@pytest.fixture
def student_token(client):
    client.post("/api/auth/register", json={
        "name": "Student One",
        "email": "student@test.edu",
        "password": "pass123",
        "role": "student",
        "roll_number": "CS001",
    })
    resp = client.post("/api/auth/login", json={
        "email": "student@test.edu",
        "password": "pass123",
    })
    return resp.json()["access_token"]


@pytest.fixture
def student2_token(client):
    client.post("/api/auth/register", json={
        "name": "Student Two",
        "email": "student2@test.edu",
        "password": "pass456",
        "role": "student",
        "roll_number": "CS002",
    })
    resp = client.post("/api/auth/login", json={
        "email": "student2@test.edu",
        "password": "pass456",
    })
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def student_headers(student_token):
    return {"Authorization": f"Bearer {student_token}"}


@pytest.fixture
def student2_headers(student2_token):
    return {"Authorization": f"Bearer {student2_token}"}


@pytest.fixture
def sample_resource(client, admin_headers):
    resp = client.post("/api/admin/resources", json={
        "name": "Test Study Room",
        "type": "study_room",
        "capacity": 10,
        "location": "Building A Room 101",
        "equipment_tags": ["Whiteboard", "Projector"],
    }, headers=admin_headers)
    return resp.json()


@pytest.fixture
def sample_lab(client, admin_headers):
    resp = client.post("/api/admin/resources", json={
        "name": "Test Lab",
        "type": "lab",
        "capacity": 25,
        "location": "CS Building Room 201",
        "equipment_tags": ["Linux Workstations", "Docker"],
    }, headers=admin_headers)
    return resp.json()
