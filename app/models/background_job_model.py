# app/models/background_job_model.py

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from app.database import Base


class BackgroundJob(Base):
    __tablename__ = "background_jobs"
    __table_args__ = (
        Index("ix_background_jobs_status_created", "status", "created_at"),
        Index("ix_background_jobs_type_status", "job_type", "status"),
    )

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="PENDING", index=True)
    file_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
