# app/middlewares/logging_middleware.py

import time
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse


async def logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()

    # Store the ID on request.state so exception handlers can include it too.
    request.state.request_id = request_id

    try:
        response = await call_next(request)
    except Exception:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        log_message = (
            f"request_id={request_id} "
            f"method={request.method} "
            f"path={request.url.path} "
            f"status_code=500 "
            f"latency_ms={latency_ms}"
        )
        print(log_message, flush=True)
        response = JSONResponse(
            status_code=500,
            content={
                "detail": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Something went wrong",
                    "request_id": request_id
                }
            }
        )
        response.headers["X-Request-ID"] = request_id
        return response

    latency_ms = round((time.time() - start_time) * 1000, 2)
    log_message = (
        f"request_id={request_id} "
        f"method={request.method} "
        f"path={request.url.path} "
        f"status_code={response.status_code} "
        f"latency_ms={latency_ms}"
    )
    print(log_message, flush=True)

    response.headers["X-Request-ID"] = request_id
    return response
