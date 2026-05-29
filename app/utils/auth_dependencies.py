# app/utils/auth_dependencies.py

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.repositories import user_repository
from app.utils.jwt_handler import verify_access_token


def get_current_user(
    token_data: dict = Depends(verify_access_token),
    db: Session = Depends(get_db)
):
    """Dependency for any authenticated user"""
    user = user_repository.get_user_by_id(db, token_data["user_id"])

    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_TOKEN",
                "message": "User is inactive or deleted"
            }
        )

    return token_data


def require_admin(token_data: dict = Depends(get_current_user)):
    """Dependency for admin-only endpoints"""
    if token_data.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail={
                "code": "FORBIDDEN",
                "message": "Admin access required"
            }
        )
    return token_data
