from app.database import Base, engine
from sqlalchemy import text

# Import models so SQLAlchemy registers every table before create_all runs.
from app.models.background_job_model import BackgroundJob  # noqa: F401
from app.models.department_model import Department  # noqa: F401
from app.models.employee_model import Employee  # noqa: F401
from app.models.user_model import User  # noqa: F401


PERFORMANCE_INDEXES = (
    "CREATE INDEX IF NOT EXISTS ix_employees_department_deleted ON employees (department_id, is_deleted)",
    "CREATE INDEX IF NOT EXISTS ix_employees_deleted_id ON employees (is_deleted, id)",
    "CREATE INDEX IF NOT EXISTS ix_employees_email_deleted ON employees (email, is_deleted)",
    "CREATE INDEX IF NOT EXISTS ix_departments_deleted_id ON departments (is_deleted, id)",
    "CREATE INDEX IF NOT EXISTS ix_users_email_deleted ON users (email, is_deleted)",
    "CREATE INDEX IF NOT EXISTS ix_users_active_deleted ON users (is_active, is_deleted)",
    "CREATE INDEX IF NOT EXISTS ix_background_jobs_status_created ON background_jobs (status, created_at)",
    "CREATE INDEX IF NOT EXISTS ix_background_jobs_type_status ON background_jobs (job_type, status)",
)


def init_db() -> None:
    with engine.begin() as connection:
        # Prevent API and Celery containers from creating tables at the same time.
        connection.execute(text("SELECT pg_advisory_lock(9001)"))
        try:
            Base.metadata.create_all(bind=connection)
            for statement in PERFORMANCE_INDEXES:
                connection.execute(text(statement))
        finally:
            connection.execute(text("SELECT pg_advisory_unlock(9001)"))


if __name__ == "__main__":
    init_db()
    print("Database tables are ready")
