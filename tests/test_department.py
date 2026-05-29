def test_create_department_success(client, admin_headers):
    response = client.post(
        "/api/v1/departments/",
        json={
            "name": "Finance",
            "description": "Finance department"
        },
        headers=admin_headers
    )

    body = response.json()

    assert response.status_code == 200
    assert body["data"]["name"] == "Finance"


def test_get_all_departments(client, user_headers, test_department):
    response = client.get("/api/v1/departments/", headers=user_headers)

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["data"]) >= 1


def test_get_department_by_id(client, user_headers, test_department):
    response = client.get(
        f"/api/v1/departments/{test_department['id']}",
        headers=user_headers
    )

    assert response.status_code == 200
    assert response.json()["data"]["id"] == test_department["id"]


def test_get_missing_department_returns_404(client, user_headers):
    response = client.get("/api/v1/departments/999", headers=user_headers)

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "DEPARTMENT_NOT_FOUND"


def test_update_department_success(client, admin_headers, test_department):
    response = client.put(
        f"/api/v1/departments/{test_department['id']}",
        json={
            "name": "Engineering Updated",
            "description": "Updated department"
        },
        headers=admin_headers
    )

    body = response.json()

    assert response.status_code == 200
    assert body["data"]["name"] == "Engineering Updated"


def test_update_department_forbidden_for_user(client, user_headers, test_department):
    response = client.put(
        f"/api/v1/departments/{test_department['id']}",
        json={
            "name": "Blocked Department",
            "description": "Should fail"
        },
        headers=user_headers
    )

    assert response.status_code == 403


def test_delete_department_soft_deletes(client, admin_headers, user_headers, test_department):
    delete_response = client.delete(
        f"/api/v1/departments/{test_department['id']}",
        headers=admin_headers
    )
    get_response = client.get(
        f"/api/v1/departments/{test_department['id']}",
        headers=user_headers
    )

    assert delete_response.status_code == 200
    assert get_response.status_code == 404


def test_missing_department_name_returns_422(client, admin_headers):
    response = client.post(
        "/api/v1/departments/",
        json={"description": "No name"},
        headers=admin_headers
    )

    assert response.status_code == 422
