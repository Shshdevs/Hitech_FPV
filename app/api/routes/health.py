from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

from app.schemas.response import ApiResponse

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get(
    "/health",
    response_model=ApiResponse[HealthResponse],
    summary="Application liveness",
    description="Confirms that the application process is running; it does not probe dependencies.",
)
async def health_check() -> ApiResponse[HealthResponse]:
    return ApiResponse(
        status_code=200,
        message="OK",
        data=HealthResponse(status="ok"),
    )
