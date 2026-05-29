from fastapi import HTTPException


def not_found_exception(resource: str):
    raise HTTPException(
        status_code=404,
        detail={
            "code": f"{resource.upper()}_NOT_FOUND",
            "message": f"{resource} not found"
        }
    )
