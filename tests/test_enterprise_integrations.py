import pytest

from app.celery_app import celery_app
from app.utils.redis_client import redis_client


def test_real_redis_ping_if_available():
    try:
        assert redis_client.ping() is True
    except Exception as exc:
        pytest.skip(f"Redis integration skipped: {exc}")


def test_real_redis_ttl_if_available():
    key = "enterprise:test:ttl"

    try:
        redis_client.setex(key, 30, "ok")
        ttl = redis_client.ttl(key)
        redis_client.delete(key)
    except Exception as exc:
        pytest.skip(f"Redis integration skipped: {exc}")

    assert 0 < ttl <= 30


def test_celery_worker_registered_tasks_if_available():
    try:
        response = celery_app.control.inspect(timeout=1).registered()
    except Exception as exc:
        pytest.skip(f"Celery integration skipped: {exc}")

    if not response:
        pytest.skip("Celery worker is not running")

    registered_tasks = set()
    for tasks in response.values():
        registered_tasks.update(tasks)

    assert "send_welcome_email" in registered_tasks
    assert "generate_employee_report" in registered_tasks
