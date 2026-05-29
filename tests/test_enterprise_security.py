from jose import jwt

from app.config import ALGORITHM, SECRET_KEY
from app.models.user_model import User
from app.utils.jwt_handler import create_access_token
from app.utils.security import hash_password
from tests.conftest import login_user, register_user


def test_public_registration_cannot_create_admin(client):
    response = register_user(
        client,
        email="public.admin@test.com",
        password="admin123",
        role="admin",
        name="Public Admin"
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "ROLE_NOT_ALLOWED"


def test_inactive_user_cannot_login(client, db_session):
    user = User(
        name="Inactive User",
        email="inactive@test.com",
        password_hash=hash_password("user123"),
        role="user",
        is_active=False,
        is_deleted=False
    )
    db_session.add(user)
    db_session.commit()

    response = login_user(client, "inactive@test.com", "user123")

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "USER_INACTIVE"


def test_deleted_user_cannot_login(client, db_session):
    user = User(
        name="Deleted User",
        email="deleted@test.com",
        password_hash=hash_password("user123"),
        role="user",
        is_active=True,
        is_deleted=True
    )
    db_session.add(user)
    db_session.commit()

    response = login_user(client, "deleted@test.com", "user123")

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_CREDENTIALS"


def test_deleted_user_token_cannot_access_protected_api(client, db_session):
    user = User(
        name="Token Deleted User",
        email="token.deleted@test.com",
        password_hash=hash_password("user123"),
        role="user",
        is_active=True,
        is_deleted=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })

    response = client.get(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"


def test_token_signed_with_wrong_secret_fails(client):
    token = jwt.encode(
        {
            "user_id": 1,
            "email": "wrong.secret@test.com",
            "role": "admin"
        },
        "wrong-secret",
        algorithm=ALGORITHM
    )

    response = client.get(
        "/api/v1/employees/",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 401
    assert response.json()["detail"]["code"] == "INVALID_TOKEN"
