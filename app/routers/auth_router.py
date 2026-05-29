# app/routers/auth_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth_schema import RegisterRequest, LoginRequest, UserResponse, TokenResponse
from app.services import auth_service
from app.config import CELERY_TASKS_ENABLED
from app.utils.response import success_response
from app.utils.auth_dependencies import get_current_user
from app.repositories import user_repository
from app.tasks.email_tasks import send_welcome_email

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=dict)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    user = auth_service.register_user(db, request)
    if CELERY_TASKS_ENABLED:
        send_welcome_email.delay(user.email, user.name)
    return success_response(
        data=UserResponse.from_orm(user).dict(),
        message="User registered successfully"
    )


@router.post("/login", response_model=dict)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    token_data = auth_service.login_user(db, request)
    return success_response(
        data=TokenResponse(**token_data).dict(),
        message="Login successful"
    )


@router.get("/me", response_model=dict)
def get_current_user_info(token_data: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    user = user_repository.get_user_by_id(db, token_data["user_id"])
    return success_response(
        data=UserResponse.from_orm(user).dict(),
        message="User info retrieved"
    )
