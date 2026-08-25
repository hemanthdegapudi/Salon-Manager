import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base

TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
app.router.on_startup.clear()
client = TestClient(app)

from app.dependencies.auth import get_current_user
from app.models.user import User, UserRole

def mock_admin_user():
    return User(
        id=1,
        username="testadmin",
        password_hash="irrelevant",
        role=UserRole.admin,
        is_active=True,
    )

app.dependency_overrides[get_current_user] = mock_admin_user

def test_login_missing_credentials():
    response = client.post("/auth/login", json={})
    assert response.status_code == 422  # FastAPI validation error

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_create_customer():
    response = client.post("/customers", json={"name": "John Doe", "phone_number": "1234567890"})
    assert response.status_code == 201
    assert response.json()["name"] == "John Doe"

def test_get_customer():
    client.post("/customers", json={"name": "Jane Doe", "phone_number": "9876543210"})
    response = client.get("/customers?phone=9876543210")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Jane Doe"
