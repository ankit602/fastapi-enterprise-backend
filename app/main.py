# app/main.py

from fastapi import FastAPI
from app.middlewares.logging_middleware import logging_middleware
from app.routers import employee_router, department_router, auth_router, metrics_router, report_router
from app.utils.exception_handler import global_exception_handler

app = FastAPI(
    title="FastAPI CRUD Practice",
    version="1.0.0"
)

app.middleware("http")(logging_middleware)
app.add_exception_handler(Exception, global_exception_handler)

app.include_router(employee_router)
app.include_router(department_router)
app.include_router(auth_router)
app.include_router(report_router)
app.include_router(metrics_router)

@app.get("/")
def root():
    return {
        "message": "FastAPI CRUD app is running"
    }
