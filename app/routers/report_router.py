# app/routers/report_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.config import CELERY_TASKS_ENABLED
from app.repositories import background_job_repository
from app.tasks.report_tasks import generate_employee_report
from app.utils.auth_dependencies import get_current_user, require_admin
from app.utils.exception import not_found_exception
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["Reports"]
)


@router.post("/employees", response_model=dict)
def create_employee_report(
    token_data: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    job = background_job_repository.create_job(db, "EMPLOYEE_REPORT")
    if CELERY_TASKS_ENABLED:
        generate_employee_report.delay(job.id)

    return success_response(
        data={
            "job_id": job.id,
            "status": job.status
        },
        message="Report generation started" if CELERY_TASKS_ENABLED else "Report job created; worker is disabled"
    )


@router.get("/{job_id}/status", response_model=dict)
def get_report_status(
    job_id: int,
    token_data: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    job = background_job_repository.get_job_by_id(db, job_id)

    if not job:
        not_found_exception("Background job")

    return success_response(
        data={
            "job_id": job.id,
            "job_type": job.job_type,
            "status": job.status,
            "file_path": job.file_path,
            "error_message": job.error_message
        }
    )
