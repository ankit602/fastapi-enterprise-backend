from app.models.background_job_model import BackgroundJob
from app.models.department_model import Department
from app.models.employee_model import Employee
from app.models.user_model import User


def _index_names(model):
    return {index.name for index in model.__table__.indexes}


def test_performance_indexes_are_registered_on_models():
    assert "ix_employees_department_deleted" in _index_names(Employee)
    assert "ix_employees_deleted_id" in _index_names(Employee)
    assert "ix_departments_deleted_id" in _index_names(Department)
    assert "ix_users_email_deleted" in _index_names(User)
    assert "ix_background_jobs_status_created" in _index_names(BackgroundJob)


def test_metrics_endpoint_reports_latency_data(client):
    client.get("/")

    response = client.get("/api/v1/metrics/")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_requests"] >= 1
    assert "p95" in data["latency_ms"]
    assert "p99" in data["latency_ms"]
