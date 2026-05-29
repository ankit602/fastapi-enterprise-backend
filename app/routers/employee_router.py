# app/routers/employee_router.py

from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.services import employee_service
from app.utils.auth_dependencies import get_current_user, require_admin
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/v1/employees",
    tags=["Employees"]
)

@router.post("/", response_model=dict)
def create_employee(
    employee: EmployeeCreate,
    token_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    result = employee_service.create_employee(db, employee)
    return success_response(
        data={
            "id": result.id,
            "name": result.name,
            "email": result.email,
            "salary": result.salary,
            "department_id": result.department_id
        },
        message="Employee created successfully"
    )

@router.get("/", response_model=dict)
def get_all_employees(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    department_id: int | None = None,
    sort_by: str = "id",
    order: Literal["asc", "desc"] = "asc",
    token_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    result = employee_service.get_all_employees(
        db=db,
        page=page,
        limit=limit,
        department_id=department_id,
        sort_by=sort_by,
        order=order
    )
    return success_response(data=result)

@router.get("/{employee_id}", response_model=dict)
def get_employee_by_id(
    employee_id: int,
    token_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    employee = employee_service.get_employee_by_id(db, employee_id)
    return success_response(data=employee)

@router.put("/{employee_id}", response_model=dict)
def update_employee(
    employee_id: int,
    employee: EmployeeUpdate,
    token_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    result = employee_service.update_employee(db, employee_id, employee)
    return success_response(data={
        "id": result.id,
        "name": result.name,
        "email": result.email,
        "salary": result.salary,
        "department_id": result.department_id
    }, message="Employee updated successfully")

@router.delete("/{employee_id}", response_model=dict)
def delete_employee(
    employee_id: int,
    token_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    employee_service.delete_employee(db, employee_id)
    return success_response(message="Employee deleted successfully")
