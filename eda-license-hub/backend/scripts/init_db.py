import asyncio
from pathlib import Path

from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models import AdminUser, LicenseServer

SAMPLES_DIR = Path(__file__).resolve().parents[1] / 'samples' / 'lmstat'
SERVERS = [
    {
        'name': 'Synopsys sample',
        'vendor': 'synopsys',
        'host': 'sample-synopsys',
        'port': 27000,
        'source_type': 'sample_file',
        'sample_path': str(SAMPLES_DIR / 'synopsys_main.txt'),
    },
    {
        'name': 'Cadence sample',
        'vendor': 'cadence',
        'host': 'sample-cadence',
        'port': 5280,
        'source_type': 'sample_file',
        'sample_path': str(SAMPLES_DIR / 'cadence_pool.txt'),
    },
]


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(LicenseServer.id))).first()
        if not existing:
            for item in SERVERS:
                session.add(LicenseServer(**item))
        admin = (await session.execute(select(AdminUser).where(AdminUser.username == 'admin'))).scalar_one_or_none()
        if admin is None:
            session.add(AdminUser(username='admin', password_hash='dev-only', email=None, is_active=True))
        await session.commit()

    print('database initialized with sample collector sources')


if __name__ == '__main__':
    asyncio.run(main())
