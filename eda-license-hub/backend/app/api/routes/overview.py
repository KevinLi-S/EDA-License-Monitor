from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.dashboard import DashboardOverview
from app.services.dashboard_service import get_dashboard_overview

router = APIRouter()


@router.get('/overview', response_model=DashboardOverview)
async def overview(session: AsyncSession = Depends(get_session)) -> DashboardOverview:
    return await get_dashboard_overview(session)
