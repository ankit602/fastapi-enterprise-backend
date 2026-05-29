def test_response_has_request_id_header(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["x-request-id"]


def test_global_exception_handler_returns_request_id(client, user_headers, monkeypatch):
    def raise_error():
        raise RuntimeError("boom")

    monkeypatch.setattr("app.services.department_service.get_all_departments", raise_error)

    response = client.get("/api/v1/departments/", headers=user_headers)

    assert response.status_code == 500
    assert response.headers["x-request-id"]
    assert response.json()["detail"]["code"] == "INTERNAL_SERVER_ERROR"
    assert response.json()["detail"]["request_id"]
