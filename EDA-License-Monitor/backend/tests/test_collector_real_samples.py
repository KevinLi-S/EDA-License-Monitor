from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import LicenseFeature, LicenseServer
from app.services.collector_service import CollectorService


SAMPLES_DIR = Path(__file__).resolve().parent.parent / 'samples' / 'lmstat'


@pytest.mark.asyncio
async def test_collect_real_lmstat_samples_into_database():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    collector = CollectorService()

    expectations = [
        ('Ansys Main', 'ansys', 'lic01', 26000, 'ansys_lic01_real.txt', 1405),
        ('Cadence Main', 'cadence', 'lic01', 28000, 'cadence_lic01_real.txt', 3287),
        ('Mentor Main', 'mentor', 'lic01', 29000, 'mentor_lic01_real.txt', 2179),
        ('Synopsys Main', 'synopsys', 'lic01', 27000, 'synopsys_lic01_real.txt', 7794),
    ]

    server_ids: list[tuple[int, int]] = []
    async with session_factory() as session:
        for name, vendor, host, port, sample_name, expected_features in expectations:
            server = LicenseServer(
                name=name,
                vendor=vendor,
                host=host,
                port=port,
                source_type='sample_file',
                sample_path=str(SAMPLES_DIR / sample_name),
            )
            session.add(server)
            await session.flush()
            server_ids.append((server.id, expected_features))
        await session.commit()

    async with session_factory() as session:
        results = await collector.collect_all(session)
        assert len(results) == 4
        assert all(result.status == 'up' for result in results)

    async with session_factory() as session:
        for server_id, expected_features in server_ids:
            server = await session.get(LicenseServer, server_id)
            assert server is not None
            assert server.last_status == 'up'
            assert server.last_error is None
            assert server.static_grants_parse_error is None
            assert server.log_parse_error is None

            features = (
                await session.execute(select(LicenseFeature).where(LicenseFeature.server_id == server_id))
            ).scalars().all()
            assert len(features) == expected_features
            assert any(feature.feature_name for feature in features)
            assert all(feature.total_licenses >= feature.used_licenses for feature in features)

    await engine.dispose()
