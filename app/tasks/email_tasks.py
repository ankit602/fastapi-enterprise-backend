# app/tasks/email_tasks.py

import smtplib
from email.message import EmailMessage

from app.celery_app import celery_app
from app.config import (
    SMTP_FROM_EMAIL,
    SMTP_FROM_NAME,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME
)


def _smtp_is_configured():
    return all([
        SMTP_HOST,
        SMTP_PORT,
        SMTP_USERNAME,
        SMTP_PASSWORD,
        SMTP_FROM_EMAIL
    ])


def _send_email(to_email: str, subject: str, body: str):
    if not _smtp_is_configured():
        print(
            f"SMTP email skipped to={to_email} reason=missing_smtp_config",
            flush=True
        )
        return

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{SMTP_FROM_NAME} <{SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USERNAME, SMTP_PASSWORD)
        smtp.send_message(message)


@celery_app.task(name="send_welcome_email")
def send_welcome_email(email: str, name: str):
    _send_email(
        to_email=email,
        subject="Welcome to FastAPI CRUD App",
        body=f"Hi {name},\n\nWelcome! Your account has been created successfully."
    )
    print(f"Welcome email task completed for {email}", flush=True)


@celery_app.task(name="send_password_reset_email")
def send_password_reset_email(email: str):
    _send_email(
        to_email=email,
        subject="Password reset request",
        body="Use the password reset link to reset your password."
    )
    print(f"Password reset email task completed for {email}", flush=True)
