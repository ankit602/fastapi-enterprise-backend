import os
import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from app.database import Base, get_db
from app.main import app
from app.models.background_job_model import BackgroundJob
from app.models.department_model import Department
from app.models.employee_model import Employee
from app.models.user_model import User
from app.tasks.email_tasks import send_welcome_email
from app.tasks.report_tasks import generate_employee_report
from app.utils.security import hash_password


TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture()
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    monkeypatch.setattr(send_welcome_email, "delay", Mock(return_value=None))
    monkeypatch.setattr(generate_employee_report, "delay", Mock(return_value=None))
    monkeypatch.setattr("app.utils.cache.get_cache", Mock(return_value=None))
    monkeypatch.setattr("app.utils.cache.set_cache", Mock(return_value=None))
    monkeypatch.setattr("app.utils.cache.delete_cache_pattern", Mock(return_value=None))

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def register_user(client, email, password="pass123", role="user", name="Test User"):
    return client.post(
        "/api/v1/auth/register",
        json={
            "name": name,
            "email": email,
            "password": password,
            "role": role
        }
    )


def login_user(client, email, password):
    return client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password
        }
    )


@pytest.fixture()
def admin_headers(client, db_session):
    email = "admin@test.com"
    password = "admin123"
    admin = User(
        name="Admin User",
        email=email,
        password_hash=hash_password(password),
        role="admin",
        is_active=True,
        is_deleted=False
    )
    db_session.add(admin)
    db_session.commit()

    response = login_user(client, email, password)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def user_headers(client):
    email = "user@test.com"
    password = "user123"
    register_user(
        client,
        email=email,
        password=password,
        role="user",
        name="Regular User"
    )
    response = login_user(client, email, password)
    token = response.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def test_department(client, admin_headers):
    response = client.post(
        "/api/v1/departments/",
        json={
            "name": "Engineering",
            "description": "Engineering department"
        },
        headers=admin_headers
    )
    return response.json()["data"]


@pytest.fixture()
def test_employee(client, admin_headers, test_department):
    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Jane Employee",
            "email": "jane.employee@test.com",
            "salary": 75000,
            "department_id": test_department["id"]
        },
        headers=admin_headers
    )
    return response.json()["data"]
