from app.models.background_job_model import BackgroundJob
from app.schemas.background_job_schema import BackgroundJobResponse


def test_background_job_response_schema_from_model():
    job = BackgroundJob(
        id=1,
        job_type="EMPLOYEE_REPORT",
        status="COMPLETED",
        file_path="reports/employees_1.csv",
        error_message=None
    )

    response = BackgroundJobResponse.model_validate(job)

    assert response.id == 1
    assert response.job_type == "EMPLOYEE_REPORT"
    assert response.status == "COMPLETED"
    assert response.file_path == "reports/employees_1.csv"
    assert response.error_message is None
