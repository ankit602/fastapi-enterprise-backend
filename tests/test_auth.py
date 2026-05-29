from datetime import datetime, timedelta

from jose import jwt

from app.config import ALGORITHM, SECRET_KEY
from app.tasks.email_tasks import send_welcome_email
from app.utils.jwt_handler import create_access_token
from app.utils.security import hash_password, verify_password
from app.utils.response import success_response
from tests.conftest import login_user, register_user


def test_password_hashing():
    password = "admin123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_access_token_contains_user_data():
    token = create_access_token({
        "user_id": 1,
        "email": "token@test.com",
        "role": "admin"
    })

    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    assert payload["user_id"] == 1
    assert payload["email"] == "token@test.com"
    assert payload["role"] == "admin"
    assert "exp" in payload


def test_success_response_shape():
    response = success_response(data={"id": 1}, message="Created")

    assert response == {
        "status": "success",
        "message": "Created",
        "data": {"id": 1}
    }


def test_register_success_queues_welcome_email(client):
    response = register_user(
        client,
        email="new.user@test.com",
        password="user123",
        role="user",
        name="New User"
    )

    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "success"
    assert body["message"] == "User registered successfully"
    assert body["data"]["email"] == "new.user@test.com"
    assert body["data"]["role"] == "user"
    send_welcome_email.delay.assert_called_once_with(
        "new.user@test.com",
        "New User"
    )


def test_register_duplicate_email_returns_400(client):
    register_user(client, email="duplicate@test.com")

    response = register_user(client, email="duplicate@test.com")

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMAIL_ALREADY_EXISTS"


def test_register_invalid_email_returns_422(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Invalid Email",
            "email": "not-an-email",
            "password": "user123",
            "role": "user"
        }
    )

    assert response.status_code == 422


def test_login_success_returns_token(client):
    register_user(client, email="login@test.com", password="user123")

    response = login_user(client, "login@test.com", "user123")

    body = response.json()

    assert response.status_code == 200
    assert body["data"]["access_token"]
    assert body["data"]["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client):
    register_user(client, email="wrong.password@test.com", password="user123")

    response = login_user(client, "wrong.password@test.com", "bad")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_me_requires_token(client):
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(client):
    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


def test_me_with_expired_token_returns_401(client):
    token = jwt.encode(
        {
            "user_id": 1,
            "email": "expired@test.com",
            "role": "user",
            "exp": datetime.utcnow() - timedelta(minutes=1)
        },
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"
