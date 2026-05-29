# app/repositories/user_repository.py

from sqlalchemy.orm import Session
from app.models.user_model import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(
        User.email == email,
        User.is_deleted == False
    ).first()


def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(
        User.id == user_id,
        User.is_deleted == False
    ).first()


def create_user(db: Session, name: str, email: str, password_hash: str, role: str):
    user = User(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
