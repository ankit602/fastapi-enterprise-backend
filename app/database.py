# app/database.py

import logging
import time

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import (
    DATABASE_URL,
    DB_MAX_OVERFLOW,
    DB_POOL_RECYCLE_SECONDS,
    DB_POOL_SIZE,
    DB_POOL_TIMEOUT,
    SLOW_QUERY_THRESHOLD_MS,
)

logger = logging.getLogger("api_logger")


def _engine_options():
    options = {
        "pool_pre_ping": True,
    }

    if DATABASE_URL and not DATABASE_URL.startswith("sqlite"):
        options.update(
            {
                "pool_size": DB_POOL_SIZE,
                "max_overflow": DB_MAX_OVERFLOW,
                "pool_timeout": DB_POOL_TIMEOUT,
                "pool_recycle": DB_POOL_RECYCLE_SECONDS,
            }
        )

    return options


engine = create_engine(DATABASE_URL, **_engine_options())


@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.perf_counter()


@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    duration_ms = round((time.perf_counter() - context._query_start_time) * 1000, 2)

    if duration_ms >= SLOW_QUERY_THRESHOLD_MS:
        compact_statement = " ".join(statement.split())
        logger.warning(
            "slow_query duration_ms=%s statement=%s",
            duration_ms,
            compact_statement[:500],
        )


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
