# app/utils/redis_client.py

import redis

from app.config import REDIS_DB, REDIS_HOST, REDIS_PORT


redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True,
    socket_connect_timeout=1,
    socket_timeout=1
)
