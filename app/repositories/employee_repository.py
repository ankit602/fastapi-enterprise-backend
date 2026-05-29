# app/repositories/employee_repository.py

from sqlalchemy.orm import Session
from app.models.department_model import Department
from app.models.employee_model import Employee
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate


def create_employee(db: Session, employee: EmployeeCreate):
    new_employee = Employee(
        name=employee.name,
        email=employee.email,
        salary=employee.salary,
        department_id=employee.department_id
    )

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


def get_employee_by_email(db: Session, email: str):
    return db.query(Employee).filter(
        Employee.email == email,
        Employee.is_deleted == False
    ).first()


def get_all_employees(
    db: Session,
    skip: int,
    limit: int,
    department_id: int | None = None,
    sort_by: str = "id",
    order: str = "asc"
):
    query = db.query(Employee).filter(Employee.is_deleted == False)

    if department_id is not None:
        query = query.filter(Employee.department_id == department_id)

    total_items = query.count()

    sort_column = getattr(Employee, sort_by, Employee.id)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    employees = query.offset(skip).limit(limit).all()

    return {
        "items": employees,
        "pagination": {
            "total_items": total_items,
            "limit": limit
        }
    }


def get_employee_by_id(db: Session, employee_id: int):
    return db.query(Employee).filter(
        Employee.id == employee_id,
        Employee.is_deleted == False
    ).first()


def update_employee(db: Session, employee_id: int, employee: EmployeeUpdate):
    existing_employee = get_employee_by_id(db, employee_id)

    if not existing_employee:
        return None

    existing_employee.name = employee.name
    existing_employee.email = employee.email
    existing_employee.salary = employee.salary
    existing_employee.department_id = employee.department_id

    db.commit()
    db.refresh(existing_employee)

    return existing_employee


def delete_employee(db: Session, employee_id: int):
    existing_employee = get_employee_by_id(db, employee_id)

    if not existing_employee:
        return None

    existing_employee.is_deleted = True
    db.commit()
    db.refresh(existing_employee)

    return existing_employee
