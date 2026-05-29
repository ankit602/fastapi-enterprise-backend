# app/tasks/report_tasks.py

import csv
import os

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models.department_model import Department
from app.models.employee_model import Employee
from app.repositories import background_job_repository


@celery_app.task(name="generate_employee_report")
def generate_employee_report(job_id: int):
    db = SessionLocal()

    try:
        background_job_repository.update_job_status(db, job_id, "IN_PROGRESS")

        os.makedirs("reports", exist_ok=True)
        file_path = os.path.join("reports", f"employees_{job_id}.csv")

        employees = (
            db.query(Employee)
            .outerjoin(Department, Employee.department_id == Department.id)
            .filter(Employee.is_deleted == False)
            .order_by(Employee.id.asc())
            .all()
        )

        with open(file_path, mode="w", newline="", encoding="utf-8") as report_file:
            writer = csv.writer(report_file)
            writer.writerow(["id", "name", "email", "salary", "department_id"])

            for employee in employees:
                writer.writerow([
                    employee.id,
                    employee.name,
                    employee.email,
                    employee.salary,
                    employee.department_id
                ])

        background_job_repository.update_job_status(
            db,
            job_id,
            "COMPLETED",
            file_path=file_path
        )
        print(f"Employee report generated job_id={job_id} file_path={file_path}", flush=True)
    except Exception as exc:
        background_job_repository.update_job_status(
            db,
            job_id,
            "FAILED",
            error_message=str(exc)
        )
        print(f"Employee report failed job_id={job_id} error={exc}", flush=True)
    finally:
        db.close()
