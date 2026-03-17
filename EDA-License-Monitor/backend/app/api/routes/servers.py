from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.schemas.server import ServerSummary
from app.services.dashboard_service import list_servers
from app.services.collector_service import collector_service

router = APIRouter()


@router.get('', response_model=list[ServerSummary])
async def get_servers(session: AsyncSession = Depends(get_session)) -> list[ServerSummary]:
    return await list_servers(session)


@router.post('/refresh')
async def refresh_servers(session: AsyncSession = Depends(get_session)) -> dict:
    results = await collector_service.collect_all(session, parallel=True)
    return {
        'status': 'ok',
        'mode': 'baseline-collection',
        'results': [result.__dict__ for result in results],
    }
