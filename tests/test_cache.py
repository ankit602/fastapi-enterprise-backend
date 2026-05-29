from unittest.mock import Mock

from redis.exceptions import RedisError

from app.services import department_service, employee_service
from app.utils import cache


def test_cache_get_returns_none_when_redis_unavailable(monkeypatch):
    monkeypatch.setattr(cache.redis_client, "ping", Mock(side_effect=RedisError("down")))

    assert cache.get_cache("missing") is None


def test_cache_set_does_not_raise_when_redis_unavailable(monkeypatch):
    monkeypatch.setattr(cache.redis_client, "ping", Mock(side_effect=RedisError("down")))

    cache.set_cache("key", {"value": 1})


def test_cache_pattern_delete_uses_scan_iter(monkeypatch):
    monkeypatch.setattr(cache, "_cache_disabled_until", 0)
    monkeypatch.setattr(cache.redis_client, "ping", Mock(return_value=True))
    scan_mock = Mock(return_value=iter(["employees:1", "employees:2"]))
    delete_mock = Mock(return_value=2)
    keys_mock = Mock()

    monkeypatch.setattr(cache.redis_client, "scan_iter", scan_mock)
    monkeypatch.setattr(cache.redis_client, "delete", delete_mock)
    monkeypatch.setattr(cache.redis_client, "keys", keys_mock)

    cache.delete_cache_pattern("employees:*")

    scan_mock.assert_called_once_with(match="employees:*", count=100)
    delete_mock.assert_called_once_with("employees:1", "employees:2")
    keys_mock.assert_not_called()


def test_employee_create_clears_employee_cache(client, admin_headers, test_department, monkeypatch):
    delete_mock = Mock()
    monkeypatch.setattr(employee_service, "delete_cache_pattern", delete_mock)

    response = client.post(
        "/api/v1/employees/",
        json={
            "name": "Cache Employee",
            "email": "cache.employee@test.com",
            "salary": 1,
            "department_id": test_department["id"]
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    delete_mock.assert_called_with("employees:*")


def test_department_create_clears_department_cache(client, admin_headers, monkeypatch):
    delete_mock = Mock()
    monkeypatch.setattr(department_service, "delete_cache_pattern", delete_mock)

    response = client.post(
        "/api/v1/departments/",
        json={
            "name": "Cache Department",
            "description": "Cache clear"
        },
        headers=admin_headers
    )

    assert response.status_code == 200
    delete_mock.assert_called_with("departments:*")
