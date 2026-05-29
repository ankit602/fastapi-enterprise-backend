# app/repositories/department_repository.py

from sqlalchemy.orm import Session
from app.models.department_model import Department
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate


def create_department(db: Session, department: DepartmentCreate):
    new_department = Department(
        name=department.name,
        description=department.description
    )

    db.add(new_department)
    db.commit()
    db.refresh(new_department)

    return new_department


def get_department_by_name(db: Session, name: str):
    return db.query(Department).filter(
        Department.name == name,
        Department.is_deleted == False
    ).first()


def get_all_departments(db: Session):
    return db.query(Department).filter(Department.is_deleted == False).all()


def get_department_by_id(db: Session, department_id: int):
    return db.query(Department).filter(
        Department.id == department_id,
        Department.is_deleted == False
    ).first()


def update_department(db: Session, department_id: int, department: DepartmentUpdate):
    existing_department = get_department_by_id(db, department_id)

    if not existing_department:
        return None

    existing_department.name = department.name
    existing_department.description = department.description

    db.commit()
    db.refresh(existing_department)

    return existing_department


def delete_department(db: Session, department_id: int):
    existing_department = get_department_by_id(db, department_id)

    if not existing_department:
        return None

    existing_department.is_deleted = True
    db.commit()
    db.refresh(existing_department)

    return existing_department
