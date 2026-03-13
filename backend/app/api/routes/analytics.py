from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.analytics import UsageTrendPoint
from app.services.dashboard_service import get_usage_trend

router = APIRouter()


@router.get('/usage-trend', response_model=list[UsageTrendPoint])
async def usage_trend(session: AsyncSession = Depends(get_session)) -> list[UsageTrendPoint]:
    return await get_usage_trend(session)
