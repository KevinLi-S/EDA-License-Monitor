from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get('/health', response_model=HealthResponse)
async def health_check(session: AsyncSession = Depends(get_session)) -> HealthResponse:
    database = 'down'
    try:
        await session.execute(text('select 1'))
        database = 'up'
    except Exception:
        database = 'down'
    return HealthResponse(status='ok' if database == 'up' else 'degraded', checks={'api': 'up', 'database': database, 'redis': 'pending', 'celery': 'pending'})
