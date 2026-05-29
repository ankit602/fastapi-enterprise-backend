from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import department_repository
from app.repositories import employee_repository
from app.schemas.employee_schema import EmployeeCreate, EmployeeUpdate
from app.utils.cache import delete_cache_pattern, get_cache, set_cache
from app.utils.exceptions import not_found_exception


def _serialize_employee(employee):
    return {
        "id": employee.id,
        "name": employee.name,
        "email": employee.email,
        "salary": employee.salary,
        "department_id": employee.department_id
    }


def create_employee(db: Session, employee: EmployeeCreate):
    existing_employee = employee_repository.get_employee_by_email(db, employee.email)
    if existing_employee:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "EMPLOYEE_EMAIL_ALREADY_EXISTS",
                "message": "Employee email already exists"
            }
        )

    if employee.department_id is not None:
        department = department_repository.get_department_by_id(db, employee.department_id)
        if not department:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_DEPARTMENT",
                    "message": "Department does not exist"
                }
            )

    result = employee_repository.create_employee(db, employee)
    delete_cache_pattern("employees:*")
    return result


def get_all_employees(
    db,
    page: int,
    limit: int,
    department_id: int | None = None,
    sort_by: str = "id",
    order: str = "asc"
):
    allowed_sort_fields = {"id", "name", "email", "salary", "department_id"}
    if sort_by not in allowed_sort_fields:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "INVALID_SORT_FIELD",
                "message": "Invalid sort field"
            }
        )

    cache_key = (
        f"employees:page:{page}:limit:{limit}:department:{department_id}:"
        f"sort:{sort_by}:order:{order}"
    )
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    skip = (page - 1) * limit

    result = employee_repository.get_all_employees(
        db=db,
        skip=skip,
        limit=limit,
        department_id=department_id,
        sort_by=sort_by,
        order=order
    )
    total_items = result["pagination"]["total_items"]
    total_pages = (total_items + limit - 1) // limit

    response_data = {
        "items": [_serialize_employee(employee) for employee in result["items"]],
        "pagination": {
            **result["pagination"],
            "page": page,
            "total_pages": total_pages
        }
    }
    set_cache(cache_key, response_data)
    return response_data


def get_employee_by_id(db: Session, employee_id: int):
    cache_key = f"employees:id:{employee_id}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    employee = employee_repository.get_employee_by_id(db, employee_id)

    if not employee:
        not_found_exception("Employee")

    response_data = _serialize_employee(employee)
    set_cache(cache_key, response_data)
    return response_data


def update_employee(db: Session, employee_id: int, employee: EmployeeUpdate):
    existing_employee = employee_repository.get_employee_by_email(db, employee.email)
    if existing_employee and existing_employee.id != employee_id:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "EMPLOYEE_EMAIL_ALREADY_EXISTS",
                "message": "Employee email already exists"
            }
        )

    if employee.department_id is not None:
        department = department_repository.get_department_by_id(db, employee.department_id)
        if not department:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "INVALID_DEPARTMENT",
                    "message": "Department does not exist"
                }
            )

    updated_employee = employee_repository.update_employee(
        db,
        employee_id,
        employee
    )

    if not updated_employee:
        not_found_exception("Employee")

    delete_cache_pattern("employees:*")
    return updated_employee


def delete_employee(db: Session, employee_id: int):
    deleted_employee = employee_repository.delete_employee(db, employee_id)

    if not deleted_employee:
        not_found_exception("Employee")

    delete_cache_pattern("employees:*")
    return {
        "message": "Employee deleted successfully"
    }
