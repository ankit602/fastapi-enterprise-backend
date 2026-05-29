from app.models.background_job_model import BackgroundJob
from app.tasks.report_tasks import generate_employee_report


def test_admin_can_create_report_job(client, admin_headers, db_session):
    response = client.post("/api/v1/reports/employees", headers=admin_headers)

    body = response.json()
    job = db_session.query(BackgroundJob).filter(
        BackgroundJob.id == body["data"]["job_id"]
    ).first()

    assert response.status_code == 200
    assert body["message"] == "Report generation started"
    assert body["data"]["status"] == "PENDING"
    assert job is not None
    assert job.job_type == "EMPLOYEE_REPORT"
    generate_employee_report.delay.assert_called_once_with(job.id)


def test_user_cannot_create_report_job(client, user_headers):
    response = client.post("/api/v1/reports/employees", headers=user_headers)

    assert response.status_code == 403


def test_get_report_status(client, admin_headers):
    create_response = client.post(
        "/api/v1/reports/employees",
        headers=admin_headers
    )
    job_id = create_response.json()["data"]["job_id"]

    response = client.get(
        f"/api/v1/reports/{job_id}/status",
        headers=admin_headers
    )

    data = response.json()["data"]

    assert response.status_code == 200
    assert data["job_id"] == job_id
    assert data["job_type"] == "EMPLOYEE_REPORT"
    assert data["status"] == "PENDING"


def test_missing_report_job_returns_404(client, admin_headers):
    response = client.get("/api/v1/reports/999/status", headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "BACKGROUND JOB_NOT_FOUND"
