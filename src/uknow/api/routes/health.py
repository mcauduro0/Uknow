"""
Health check endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Check API health status.

    Returns service status, version, and name.
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        service="uknow-api",
    )


@router.get("/ready")
async def readiness_check() -> dict:
    """
    Check if the service is ready to accept requests.

    This can be extended to check database connections,
    external service availability, etc.
    """
    return {"ready": True}
