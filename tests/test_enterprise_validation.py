def test_duplicate_employee_email_returns_400(client, admin_headers, test_department):
    payload = {
        "name": "Duplicate Employee",
        "email": "duplicate.employee@test.com",
        "salary": 100,
        "department_id": test_department["id"]
    }
    client.post("/api/v1/employees/", json=payload, headers=admin_headers)

    response = client.post("/api/v1/employees/", json=payload, headers=admin_headers)

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "EMPLOYEE_EMAIL_ALREADY_EXISTS"


def test_duplicate_department_name_returns_400(client, admin_headers):
    payload = {
        "name": "Duplicate Department",
        "description": "Duplicate"
    }
    client.post("/api/v1/departments/", json=payload, headers=admin_headers)

    response = client.post("/api/v1/departments/", json=payload, headers=admin_headers)

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "DEPARTMENT_ALREADY_EXISTS"


def test_employee_invalid_department_returns_400(client, admin_headers):
    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Invalid Department Employee",
            "email": "invalid.department@test.com",
            "salary": 100,
            "department_id": 999
        },
        headers=admin_headers
    )

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_DEPARTMENT"


def test_negative_salary_returns_422(client, admin_headers, test_department):
    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Negative Salary",
            "email": "negative.salary@test.com",
            "salary": -1,
            "department_id": test_department["id"]
        },
        headers=admin_headers
    )

    assert response.status_code == 422


def test_empty_department_name_returns_422(client, admin_headers):
    response = client.post(
        "/api/v1/departments/",
        json={
            "name": "",
            "description": "Empty name"
        },
        headers=admin_headers
    )

    assert response.status_code == 422


def test_invalid_page_returns_422(client, user_headers):
    response = client.get("/api/v1/employees/?page=0", headers=user_headers)

    assert response.status_code == 422


def test_invalid_limit_returns_422(client, user_headers):
    response = client.get("/api/v1/employees/?limit=0", headers=user_headers)

    assert response.status_code == 422


def test_too_large_limit_returns_422(client, user_headers):
    response = client.get("/api/v1/employees/?limit=101", headers=user_headers)

    assert response.status_code == 422


def test_invalid_order_returns_422(client, user_headers):
    response = client.get("/api/v1/employees/?order=random", headers=user_headers)

    assert response.status_code == 422


def test_invalid_sort_field_returns_400(client, user_headers):
    response = client.get("/api/v1/employees/?sort_by=random", headers=user_headers)

    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "INVALID_SORT_FIELD"


def test_malformed_json_returns_422(client, admin_headers):
    response = client.post(
        "/api/v1/departments/",
        content="{bad json",
        headers={
            **admin_headers,
            "Content-Type": "application/json"
        }
    )

    assert response.status_code == 422
