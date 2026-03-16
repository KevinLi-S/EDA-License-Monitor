from app.core.celery_app import celery_app
from app.database import AsyncSessionLocal
from app.services.collector_service import collector_service


@celery_app.task(name='app.tasks.collectors.collect_license_snapshots')
def collect_license_snapshots() -> dict:
    import asyncio

    async def _run() -> dict:
        async with AsyncSessionLocal() as session:
            results = await collector_service.collect_all(session)
            return {'status': 'ok', 'results': [result.__dict__ for result in results]}

    return asyncio.run(_run())
