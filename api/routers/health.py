"""
Health Check Router
===================

Basic health check endpoint for API monitoring.
This is essential for production deployments.
"""

from fastapi import APIRouter
from datetime import datetime

from api.models.schemas import HealthResponse


router = APIRouter(prefix="/health", tags=["Health"])


@router.get(
    "",
    response_model=HealthResponse,
    summary="API Health Check",
    description="Check if the API is running and healthy."
)
async def health_check():
    """
    Check API health status.
    
    Returns basic health information including:
    - Status (healthy/unhealthy)
    - Current timestamp
    - API version
    - Environment
    """
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version="1.0.0",
        environment="development"
    )
