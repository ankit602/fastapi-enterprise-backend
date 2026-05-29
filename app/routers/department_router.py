# app/routers/department_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate
from app.services import department_service
from app.utils.auth_dependencies import get_current_user, require_admin
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/v1/departments",
    tags=["Departments"]
)

@router.post("/", response_model=dict)
def create_department(
    department: DepartmentCreate,
    token_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    result = department_service.create_department(db, department)
    return success_response(
        data={
            "id": result.id,
            "name": result.name,
            "description": result.description
        },
        message="Department created successfully"
    )

@router.get("/", response_model=dict)
def get_all_departments(
    token_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    departments = department_service.get_all_departments(db)
    return success_response(data=departments)

@router.get("/{department_id}", response_model=dict)
def get_department_by_id(
    department_id: int,
    token_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    department = department_service.get_department_by_id(db, department_id)
    return success_response(data=department)

@router.put("/{department_id}", response_model=dict)
def update_department(
    department_id: int,
    department: DepartmentUpdate,
    token_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    result = department_service.update_department(db, department_id, department)
    return success_response(
        data={
            "id": result.id,
            "name": result.name,
            "description": result.description
        },
        message="Department updated successfully"
    )

@router.delete("/{department_id}", response_model=dict)
def delete_department(
    department_id: int,
    token_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    department_service.delete_department(db, department_id)
    return success_response(message="Department deleted successfully")
