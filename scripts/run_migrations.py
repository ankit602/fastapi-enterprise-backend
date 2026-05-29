# scripts/run_migrations.py

from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from app.config import DATABASE_URL
from sqlalchemy import create_engine

MIGRATIONS_DIR = ROOT_DIR / "migrations"
MIGRATION_FILES = [
    "001_create_departments.sql",
    "002_add_employee_columns.sql",
    "003_add_department_description.sql",
    "004_seed_departments.sql",
    "005_fix_employee_data.sql",
    "006_add_foreign_key.sql",
    "007_create_users.sql"
]


def run_sql_file(engine, path: Path):
    print(f"Applying {path.name}...")
    sql = path.read_text(encoding="utf-8")
    with engine.begin() as conn:
        conn.exec_driver_sql(sql)
    print(f"Applied {path.name}")


def main():
    engine = create_engine(DATABASE_URL)

    for filename in MIGRATION_FILES:
        path = MIGRATIONS_DIR / filename
        if not path.exists():
            print(f"Migration file missing: {path}")
            sys.exit(1)
        run_sql_file(engine, path)

    print("All migrations applied successfully.")


if __name__ == "__main__":
    main()
