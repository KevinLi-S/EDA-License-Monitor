import asyncio
from pathlib import Path

from sqlalchemy import select

from app.database import AsyncSessionLocal, Base, engine
from app.models import AdminUser, LicenseServer

SAMPLES_DIR = Path(__file__).resolve().parents[1] / 'samples' / 'lmstat'
SERVERS = [
    {
        'name': 'Synopsys lic01',
        'vendor': 'synopsys',
        'host': 'lic01',
        'port': 27000,
        'source_type': 'sample_file',
        'sample_path': str(SAMPLES_DIR / 'synopsys_lic01_real.txt'),
    },
    {
        'name': 'Cadence lic01',
        'vendor': 'cadence',
        'host': 'lic01',
        'port': 28000,
        'source_type': 'sample_file',
        'sample_path': str(SAMPLES_DIR / 'cadence_lic01_real.txt'),
    },
    {
        'name': 'Mentor lic01',
        'vendor': 'mentor',
        'host': 'lic01',
        'port': 29000,
        'source_type': 'sample_file',
        'sample_path': str(SAMPLES_DIR / 'mentor_lic01_real.txt'),
    },
    {
        'name': 'Ansys lic01',
        'vendor': 'ansys',
        'host': 'lic01',
        'port': 26000,
        'source_type': 'sample_file',
        'sample_path': str(SAMPLES_DIR / 'ansys_lic01_real.txt'),
    },
]


async def main() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        existing_servers = (await session.execute(select(LicenseServer))).scalars().all()
        existing_by_name = {server.name: server for server in existing_servers}
        target_names = {item['name'] for item in SERVERS}

        for server in existing_servers:
            if server.name not in target_names:
                await session.delete(server)

        for item in SERVERS:
            existing = existing_by_name.get(item['name'])
            if existing is None:
                session.add(LicenseServer(**item))
            else:
                for key, value in item.items():
                    setattr(existing, key, value)

        admin = (await session.execute(select(AdminUser).where(AdminUser.username == 'admin'))).scalar_one_or_none()
        if admin is None:
            session.add(AdminUser(username='admin', password_hash='dev-only', email=None, is_active=True))
        await session.commit()

    print('database initialized with sample collector sources')


if __name__ == '__main__':
    asyncio.run(main())
