"""Health check endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.database import get_session
from app.config import settings
import redis.asyncio as aioredis

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_session)):
    """
    Comprehensive health check endpoint
    Checks database, Redis, and Celery connectivity
    """
    checks = {
        "status": "healthy",
        "database": "unknown",
        "redis": "unknown",
        "celery": "unknown"
    }

    # Check PostgreSQL
    try:
        result = await db.execute(text("SELECT 1"))
        if result:
            checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        checks["status"] = "degraded"

    # Check Redis
    try:
        redis_client = aioredis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        checks["redis"] = "healthy"
        await redis_client.close()
    except Exception as e:
        checks["redis"] = f"unhealthy: {str(e)}"
        checks["status"] = "degraded"

    # Celery check placeholder (will check worker status later)
    checks["celery"] = "not_implemented"

    return checks


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe - simple check if app is running
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_probe(db: AsyncSession = Depends(get_session)):
    """
    Kubernetes readiness probe - check if app can serve traffic
    """
    try:
        # Quick database check
        await db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}
