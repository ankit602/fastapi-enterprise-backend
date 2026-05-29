from app.database import Base, engine
from sqlalchemy import text

# Import models so SQLAlchemy registers every table before create_all runs.
from app.models.background_job_model import BackgroundJob  # noqa: F401
from app.models.department_model import Department  # noqa: F401
from app.models.employee_model import Employee  # noqa: F401
from app.models.user_model import User  # noqa: F401


def init_db() -> None:
    with engine.begin() as connection:
        # Prevent API and Celery containers from creating tables at the same time.
        connection.execute(text("SELECT pg_advisory_lock(9001)"))
        try:
            Base.metadata.create_all(bind=connection)
        finally:
            connection.execute(text("SELECT pg_advisory_unlock(9001)"))


if __name__ == "__main__":
    init_db()
    print("Database tables are ready")
