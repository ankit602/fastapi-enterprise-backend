# app/repositories/background_job_repository.py

from sqlalchemy.orm import Session

from app.models.background_job_model import BackgroundJob


def create_job(db: Session, job_type: str):
    job = BackgroundJob(
        job_type=job_type,
        status="PENDING"
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_by_id(db: Session, job_id: int):
    return db.query(BackgroundJob).filter(BackgroundJob.id == job_id).first()


def update_job_status(
    db: Session,
    job_id: int,
    status: str,
    file_path: str | None = None,
    error_message: str | None = None
):
    job = get_job_by_id(db, job_id)

    if not job:
        return None

    job.status = status
    job.file_path = file_path
    job.error_message = error_message
    db.commit()
    db.refresh(job)
    return job
