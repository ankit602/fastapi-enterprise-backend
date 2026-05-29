# app/services/auth_service.py

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories import user_repository
from app.schemas.auth_schema import RegisterRequest, LoginRequest
from app.utils.security import hash_password, verify_password
from app.utils.jwt_handler import create_access_token


def register_user(db: Session, request: RegisterRequest):
    if request.role != "user":
        raise HTTPException(
            status_code=403,
            detail={
                "code": "ROLE_NOT_ALLOWED",
                "message": "Public registration is allowed only for user role"
            }
        )

    existing_user = user_repository.get_user_by_email(db, request.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "EMAIL_ALREADY_EXISTS",
                "message": "Email already registered"
            }
        )

    hashed_password = hash_password(request.password)
    return user_repository.create_user(
        db=db,
        name=request.name,
        email=request.email,
        password_hash=hashed_password,
        role=request.role
    )


def login_user(db: Session, request: LoginRequest):
    user = user_repository.get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )

    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password"
            }
        )

    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "USER_INACTIVE",
                "message": "User account is inactive"
            }
        )

    token = create_access_token({
        "user_id": user.id,
        "email": user.email,
        "role": user.role
    })
    return {
        "access_token": token,
        "token_type": "bearer"
    }
