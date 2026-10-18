from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.services.cache_service import cache_service

router = APIRouter()

@router.get("/health", response_model=HealthResponse, summary="System Health Check")
async def health_check():
    redis_alive = await cache_service.is_healthy()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        redis_connected=redis_alive
    )
