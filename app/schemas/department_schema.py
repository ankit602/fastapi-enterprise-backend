# app/schemas/department_schema.py

from pydantic import BaseModel, Field


class DepartmentCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class DepartmentUpdate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class DepartmentResponse(BaseModel):
    id: int
    name: str
    description: str | None

    class Config:
        from_attributes = True
