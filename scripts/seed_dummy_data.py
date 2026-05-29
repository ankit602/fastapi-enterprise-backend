# scripts/seed_dummy_data.py

from pathlib import Path
import random
import sys

root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

from app.database import SessionLocal, engine, Base
from app.models.department_model import Department
from app.models.employee_model import Employee

try:
    from faker import Faker
    fake = Faker()
except ImportError:
    fake = None

DEPARTMENTS = [
    "Engineering",
    "Sales",
    "Marketing",
    "Human Resources",
    "Finance"
]

EMPLOYEES_PER_DEPARTMENT = 20


def generate_employee_name(email_index: int):
    if fake:
        return fake.name()

    first_names = [
        "Alex", "Jordan", "Taylor", "Morgan", "Casey",
        "Jamie", "Reese", "Avery", "Riley", "Skyler"
    ]
    last_names = [
        "Lee", "Patel", "Kim", "Robinson", "Clark",
        "Adams", "Bell", "Bailey", "Brooks", "Gray"
    ]
    return f"{random.choice(first_names)} {random.choice(last_names)}"


def generate_employee_email(name: str, index: int):
    if fake:
        return fake.unique.email()
    local = name.lower().replace(" ", ".")
    return f"{local}.{index}@example.com"


def seed():
    print("Starting dummy data seeding...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_dept_count = db.query(Department).filter(Department.is_deleted == False).count()
        if existing_dept_count > 0:
            print("Existing departments found, skipping seed to avoid duplicates.")
            return

        departments = []
        for dept_name in DEPARTMENTS:
            department = Department(name=dept_name)
            db.add(department)
            departments.append(department)

        db.flush()

        employee_count = 0
        for idx, department in enumerate(departments, start=1):
            for employee_index in range(1, EMPLOYEES_PER_DEPARTMENT + 1):
                name = generate_employee_name(employee_count + employee_index)
                email = generate_employee_email(name, employee_count + employee_index)
                salary = random.randint(40000, 120000)

                employee = Employee(
                    name=name,
                    email=email,
                    salary=salary,
                    department_id=department.id
                )
                db.add(employee)
                employee_count += 1

        db.commit()
        print(f"Seeded {len(departments)} departments and {employee_count} employees.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
