from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import department_repository
from app.schemas.department_schema import DepartmentCreate, DepartmentUpdate
from app.utils.cache import delete_cache_pattern, get_cache, set_cache
from app.utils.exception import not_found_exception


def _serialize_department(department):
    return {
        "id": department.id,
        "name": department.name,
        "description": department.description
    }


def create_department(db: Session, department: DepartmentCreate):
    existing_department = department_repository.get_department_by_name(db, department.name)
    if existing_department:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "DEPARTMENT_ALREADY_EXISTS",
                "message": "Department name already exists"
            }
        )

    result = department_repository.create_department(db, department)
    delete_cache_pattern("departments:*")
    return result


def get_all_departments(db: Session):
    cache_key = "departments:all"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    departments = department_repository.get_all_departments(db)
    response_data = [_serialize_department(department) for department in departments]
    set_cache(cache_key, response_data)
    return response_data


def get_department_by_id(db: Session, department_id: int):
    cache_key = f"departments:id:{department_id}"
    cached_data = get_cache(cache_key)
    if cached_data:
        return cached_data

    department = department_repository.get_department_by_id(db, department_id)
    if not department:
        not_found_exception("Department")

    response_data = _serialize_department(department)
    set_cache(cache_key, response_data)
    return response_data


def update_department(db: Session, department_id: int, department: DepartmentUpdate):
    existing_department = department_repository.get_department_by_name(db, department.name)
    if existing_department and existing_department.id != department_id:
        raise HTTPException(
            status_code=400,
            detail={
                "code": "DEPARTMENT_ALREADY_EXISTS",
                "message": "Department name already exists"
            }
        )

    updated_department = department_repository.update_department(db, department_id, department)
    if not updated_department:
        not_found_exception("Department")

    delete_cache_pattern("departments:*")
    return updated_department


def delete_department(db: Session, department_id: int):
    deleted_department = department_repository.delete_department(db, department_id)
    if not deleted_department:
        not_found_exception("Department")

    delete_cache_pattern("departments:*")
    return deleted_department
