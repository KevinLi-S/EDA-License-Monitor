import json
from pathlib import Path

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import LicenseFeature, LicenseFileAsset, LicenseLogEvent, LicenseServer, StaticLicenseGrant
from app.services.collector_service import CollectorService


STATIC_SAMPLES_DIR = Path(__file__).resolve().parent.parent / 'samples' / 'static_assets'
CASES = sorted(
    path for path in (STATIC_SAMPLES_DIR.iterdir() if STATIC_SAMPLES_DIR.exists() else [])
    if path.is_dir() and (path / 'manifest.json').exists() and (path / 'license.dat').exists()
)


@pytest.mark.skipif(not CASES, reason='No real static asset sample cases have been added yet.')
@pytest.mark.asyncio
async def test_collect_real_static_asset_samples_into_database():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    collector = CollectorService()

    async with session_factory() as session:
        for case_dir in CASES:
            manifest = json.loads((case_dir / 'manifest.json').read_text(encoding='utf-8'))
            server_name = manifest.get('server_name') or case_dir.name
            vendor_name = manifest.get('vendor_name') or case_dir.name
            license_path = case_dir / 'license.dat'
            log_path = case_dir / 'license.log'

            session.add(LicenseServer(
                name=f'{vendor_name} {server_name}',
                vendor=vendor_name,
                host=server_name,
                port=27000,
                source_type='sample_file',
                sample_path=str(case_dir / 'collector_sample.txt'),
                license_file_path=str(license_path),
                license_log_path=str(log_path) if log_path.exists() else None,
            ))
        await session.commit()

    async with session_factory() as session:
        servers = (await session.execute(select(LicenseServer).order_by(LicenseServer.id))).scalars().all()
        for server, case_dir in zip(servers, CASES, strict=False):
            license_path = case_dir / 'license.dat'
            sample_text = '\n'.join([
                f'License server status: {server.port}@{server.host}',
                f'    License file(s) on {server.host}: {license_path}:',
                f'{server.host}: license server UP v11.19',
                f'{server.vendor}: UP v11.19',
                'Users of PLACEHOLDER:  (Total of 0 licenses issued;  Total of 0 licenses in use)',
            ])
            (case_dir / 'collector_sample.txt').write_text(sample_text, encoding='utf-8')
            server.sample_path = str(case_dir / 'collector_sample.txt')
        await session.commit()

    async with session_factory() as session:
        results = await collector.collect_all(session)
        assert len(results) == len(CASES)
        assert all(result.status == 'up' for result in results)

    async with session_factory() as session:
        servers = (await session.execute(select(LicenseServer).order_by(LicenseServer.id))).scalars().all()
        for server, case_dir in zip(servers, CASES, strict=False):
            manifest = json.loads((case_dir / 'manifest.json').read_text(encoding='utf-8'))

            asset = (await session.execute(select(LicenseFileAsset).where(LicenseFileAsset.server_id == server.id))).scalar_one()
            grants = (await session.execute(select(StaticLicenseGrant).where(StaticLicenseGrant.server_id == server.id))).scalars().all()
            events = (await session.execute(select(LicenseLogEvent).where(LicenseLogEvent.server_id == server.id))).scalars().all()
            features = (await session.execute(select(LicenseFeature).where(LicenseFeature.server_id == server.id))).scalars().all()

            assert asset.server_name == manifest.get('server_name')
            assert asset.daemon_name == manifest.get('vendor_name')
            assert len(grants) >= manifest.get('expected_grants_min', 1)
            assert len(features) == 1
            assert features[0].feature_name == 'PLACEHOLDER'

            expected_events_min = manifest.get('expected_events_min', 0)
            if expected_events_min > 0:
                assert len(events) >= expected_events_min
            else:
                assert len(events) == 0

    await engine.dispose()
