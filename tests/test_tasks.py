from pathlib import Path
from unittest.mock import Mock

from app.models.background_job_model import BackgroundJob
from app.models.employee_model import Employee
from app.tasks import email_tasks
from app.tasks import report_tasks
from app.tasks.report_tasks import generate_employee_report


def test_email_task_skips_when_smtp_missing(monkeypatch):
    monkeypatch.setattr(email_tasks, "SMTP_HOST", "")
    monkeypatch.setattr(email_tasks, "SMTP_USERNAME", "")
    monkeypatch.setattr(email_tasks, "SMTP_PASSWORD", "")
    monkeypatch.setattr(email_tasks, "SMTP_FROM_EMAIL", "")

    email_tasks.send_welcome_email.run("skip@test.com", "Skip User")


def test_email_task_uses_smtp_when_configured(monkeypatch):
    smtp_instance = Mock()
    smtp_context = Mock()
    smtp_context.__enter__ = Mock(return_value=smtp_instance)
    smtp_context.__exit__ = Mock(return_value=None)
    smtp_class = Mock(return_value=smtp_context)

    monkeypatch.setattr(email_tasks, "SMTP_HOST", "smtp.test.com")
    monkeypatch.setattr(email_tasks, "SMTP_PORT", 587)
    monkeypatch.setattr(email_tasks, "SMTP_USERNAME", "sender@test.com")
    monkeypatch.setattr(email_tasks, "SMTP_PASSWORD", "password")
    monkeypatch.setattr(email_tasks, "SMTP_FROM_EMAIL", "sender@test.com")
    monkeypatch.setattr(email_tasks.smtplib, "SMTP", smtp_class)

    email_tasks.send_welcome_email.run("receiver@test.com", "Receiver")

    smtp_class.assert_called_once_with("smtp.test.com", 587)
    smtp_instance.starttls.assert_called_once()
    smtp_instance.login.assert_called_once_with("sender@test.com", "password")
    smtp_instance.send_message.assert_called_once()


def test_generate_employee_report_creates_csv_and_completes_job(
    db_session,
    monkeypatch,
    tmp_path
):
    job = BackgroundJob(job_type="EMPLOYEE_REPORT", status="PENDING")
    employee = Employee(
        name="Report Employee",
        email="report.employee@test.com",
        salary=12345,
        department_id=None
    )
    db_session.add(job)
    db_session.add(employee)
    db_session.commit()
    db_session.refresh(job)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(report_tasks, "SessionLocal", Mock(return_value=db_session))

    generate_employee_report.run(job.id)
    updated_job = db_session.query(BackgroundJob).filter(
        BackgroundJob.id == job.id
    ).first()

    report_path = tmp_path / updated_job.file_path

    assert updated_job.status == "COMPLETED"
    assert report_path.exists()
    assert "report.employee@test.com" in report_path.read_text()


def test_generate_employee_report_marks_failed(monkeypatch, db_session):
    job = BackgroundJob(job_type="EMPLOYEE_REPORT", status="PENDING")
    db_session.add(job)
    db_session.commit()
    db_session.refresh(job)
    monkeypatch.setattr(report_tasks, "SessionLocal", Mock(return_value=db_session))

    def broken_makedirs(*args, **kwargs):
        raise RuntimeError("report failure")

    monkeypatch.setattr("app.tasks.report_tasks.os.makedirs", broken_makedirs)

    generate_employee_report.run(job.id)
    updated_job = db_session.query(BackgroundJob).filter(
        BackgroundJob.id == job.id
    ).first()

    assert updated_job.status == "FAILED"
    assert "report failure" in updated_job.error_message
