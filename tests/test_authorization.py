def test_admin_can_create_employee(client, admin_headers, test_department):
    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Admin Employee",
            "email": "admin.employee@test.com",
            "salary": 50000,
            "department_id": test_department["id"]
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Employee created successfully"


def test_user_cannot_create_employee(client, user_headers, test_department):
    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Blocked Employee",
            "email": "blocked.employee@test.com",
            "salary": 50000,
            "department_id": test_department["id"]
        },
        headers=user_headers
    )

    assert response.status_code == 403
    assert response.json()["detail"]["code"] == "FORBIDDEN"


def test_user_can_read_employees(client, user_headers):
    response = client.get("/api/v1/employees/", headers=user_headers)

    assert response.status_code == 200


def test_anonymous_cannot_read_employees(client):
    response = client.get("/api/v1/employees/")

    assert response.status_code == 401


def test_admin_can_create_department(client, admin_headers):
    response = client.post(
        "/api/v1/departments/",
        json={
            "name": "Admin Department",
            "description": "Created by admin"
        },
        headers=admin_headers
    )

    assert response.status_code == 200


def test_user_cannot_create_department(client, user_headers):
    response = client.post(
        "/api/v1/departments/",
        json={
            "name": "Blocked Department",
            "description": "Should fail"
        },
        headers=user_headers
    )

    assert response.status_code == 403


def test_user_can_read_departments(client, user_headers):
    response = client.get("/api/v1/departments/", headers=user_headers)

    assert response.status_code == 200


def test_anonymous_cannot_read_departments(client):
    response = client.get("/api/v1/departments/")

    assert response.status_code == 401


def test_admin_can_start_report(client, admin_headers):
    response = client.post("/api/v1/reports/employees", headers=admin_headers)

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "PENDING"


def test_user_cannot_start_report(client, user_headers):
    response = client.post("/api/v1/reports/employees", headers=user_headers)

    assert response.status_code == 403
