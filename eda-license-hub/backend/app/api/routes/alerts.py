from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.alert import AlertSummary
from app.services.dashboard_service import list_alerts

router = APIRouter()


@router.get('', response_model=list[AlertSummary])
async def get_alerts(session: AsyncSession = Depends(get_session)) -> list[AlertSummary]:
    return await list_alerts(session)
