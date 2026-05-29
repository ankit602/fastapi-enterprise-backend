def test_create_employee_success(client, admin_headers, test_department):
    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Employee Create",
            "email": "employee.create@test.com",
            "salary": 60000,
            "department_id": test_department["id"]
        },
        headers=admin_headers
    )

    body = response.json()

    assert response.status_code == 200
    assert body["data"]["email"] == "employee.create@test.com"
    assert body["data"]["department_id"] == test_department["id"]


def test_get_all_employees_includes_pagination(client, user_headers, test_employee):
    response = client.get(
        "/api/v1/employees/?page=1&limit=10&sort_by=id&order=asc",
        headers=user_headers
    )

    data = response.json()["data"]

    assert response.status_code == 200
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["limit"] == 10
    assert data["pagination"]["total_pages"] >= 1


def test_filter_employees_by_department(client, user_headers, test_employee):
    department_id = test_employee["department_id"]

    response = client.get(
        f"/api/v1/employees/?department_id={department_id}",
        headers=user_headers
    )

    items = response.json()["data"]["items"]

    assert response.status_code == 200
    assert all(item["department_id"] == department_id for item in items)


def test_get_employee_by_id(client, user_headers, test_employee):
    response = client.get(
        f"/api/v1/employees/{test_employee['id']}",
        headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["data"]["id"] == test_employee["id"]


def test_get_missing_employee_returns_404(client, user_headers):
    response = client.get("/api/v1/employees/999", headers=user_headers)

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "EMPLOYEE_NOT_FOUND"


def test_update_employee_success(client, admin_headers, test_employee):
    response = client.put(
        f"/api/v1/employees/{test_employee['id']}",
        json={
            "name": "Employee Updated",
            "email": "employee.updated@test.com",
            "salary": 90000,
            "department_id": test_employee["department_id"]
        },
        headers=admin_headers
    )

    body = response.json()

    assert response.status_code == 200
    assert body["data"]["name"] == "Employee Updated"
    assert body["data"]["salary"] == 90000


def test_update_employee_forbidden_for_user(client, user_headers, test_employee):
    response = client.put(
        f"/api/v1/employees/{test_employee['id']}",
        json={
            "name": "Blocked Update",
            "email": "blocked.update@test.com",
            "salary": 1,
            "department_id": test_employee["department_id"]
        },
        headers=user_headers
    )

    assert response.status_code == 403


def test_delete_employee_soft_deletes(client, admin_headers, user_headers, test_employee):
    delete_response = client.delete(
        f"/api/v1/employees/{test_employee['id']}",
        headers=admin_headers
    )
    get_response = client.get(
        f"/api/v1/employees/{test_employee['id']}",
        headers=user_headers
    )

    assert delete_response.status_code == 200
    assert get_response.status_code == 404


def test_invalid_employee_email_returns_422(client, admin_headers, test_department):
    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Invalid Email",
            "email": "bad-email",
            "salary": 1,
            "department_id": test_department["id"]
        },
        headers=admin_headers
    )

    assert response.status_code == 422
