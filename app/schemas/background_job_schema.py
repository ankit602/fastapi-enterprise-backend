# app/schemas/background_job_schema.py

from pydantic import BaseModel


class BackgroundJobResponse(BaseModel):
    id: int
    job_type: str
    status: str
    file_path: str | None = None
    error_message: str | None = None

    class Config:
        from_attributes = True
