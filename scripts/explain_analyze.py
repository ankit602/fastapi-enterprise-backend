import sys
from pathlib import Path

from sqlalchemy import text

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.database import engine


QUERIES = {
    "employees_list": """
        EXPLAIN ANALYZE
        SELECT id, name, email, salary, department_id
        FROM employees
        WHERE is_deleted = false
        ORDER BY id ASC
        LIMIT 10 OFFSET 0
    """,
    "employees_by_department": """
        EXPLAIN ANALYZE
        SELECT id, name, email, salary, department_id
        FROM employees
        WHERE is_deleted = false AND department_id = 1
        ORDER BY id ASC
        LIMIT 10 OFFSET 0
    """,
    "department_list": """
        EXPLAIN ANALYZE
        SELECT id, name, description
        FROM departments
        WHERE is_deleted = false
        ORDER BY id ASC
    """,
    "login_lookup": """
        EXPLAIN ANALYZE
        SELECT id, email, password_hash, role
        FROM users
        WHERE email = 'admin@test.com' AND is_deleted = false
        LIMIT 1
    """,
}


def main() -> None:
    with engine.connect() as connection:
        for name, statement in QUERIES.items():
            print(f"\n--- {name} ---")
            rows = connection.execute(text(statement)).fetchall()
            for row in rows:
                print(row[0])


if __name__ == "__main__":
    main()
