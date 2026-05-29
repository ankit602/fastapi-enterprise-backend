from app.routers.department_router import router as department_router
from app.routers.employee_router import router as employee_router
from app.routers.auth_router import router as auth_router
from app.routers.metrics_router import router as metrics_router
from app.routers.report_router import router as report_router

__all__ = [
    "employee_router",
    "department_router",
    "auth_router",
    "metrics_router",
    "report_router"
]
