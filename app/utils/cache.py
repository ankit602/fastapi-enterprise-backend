# app/utils/cache.py

import json
import logging
import time

from redis.exceptions import RedisError

from app.config import CACHE_TTL_SECONDS
from app.utils.redis_client import redis_client

logger = logging.getLogger("api_logger")
_cache_disabled_until = 0


def _cache_is_available():
    global _cache_disabled_until

    if time.time() < _cache_disabled_until:
        return False

    try:
        redis_client.ping()
        return True
    except RedisError as exc:
        _cache_disabled_until = time.time() + 30
        logger.warning("cache_unavailable error=%s", exc)
        return False


def get_cache(key: str):
    if not _cache_is_available():
        return None

    try:
        cached_data = redis_client.get(key)
    except RedisError as exc:
        logger.warning("cache_get_failed key=%s error=%s", key, exc)
        return None

    if cached_data:
        return json.loads(cached_data)

    return None


def set_cache(key: str, value, ttl: int = CACHE_TTL_SECONDS):
    if not _cache_is_available():
        return

    try:
        redis_client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )
    except RedisError as exc:
        logger.warning("cache_set_failed key=%s error=%s", key, exc)


def delete_cache(key: str):
    if not _cache_is_available():
        return

    try:
        redis_client.delete(key)
    except RedisError as exc:
        logger.warning("cache_delete_failed key=%s error=%s", key, exc)


def delete_cache_pattern(pattern: str):
    if not _cache_is_available():
        return

    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except RedisError as exc:
        logger.warning("cache_delete_pattern_failed pattern=%s error=%s", pattern, exc)
