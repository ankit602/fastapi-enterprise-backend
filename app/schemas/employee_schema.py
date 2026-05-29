# app/schemas/employee_schema.py

from pydantic import BaseModel, EmailStr, Field

class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    salary: int | None = Field(default=None, ge=0)
    department_id: int | None = None

class EmployeeUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    salary: int | None = Field(default=None, ge=0)
    department_id: int | None = None

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    salary: int | None
    department_id: int | None

    class Config:
        from_attributes = True
