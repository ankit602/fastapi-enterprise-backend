from fastapi import APIRouter

from app.utils.metrics import get_metrics_snapshot
from app.utils.response import success_response

router = APIRouter(
    prefix="/api/v1/metrics",
    tags=["Metrics"]
)


@router.get("/")
def get_metrics():
    return success_response(
        message="Metrics fetched successfully",
        data=get_metrics_snapshot()
    )
