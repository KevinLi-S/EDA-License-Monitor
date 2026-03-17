from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base
from app.models import LicenseFeature, LicenseFileAsset, LicenseLogEvent, LicenseServer, StaticLicenseGrant
from app.services.collector_service import CollectorService


@pytest.mark.asyncio
async def test_collect_single_persists_snapshot_and_static_assets(tmp_path):
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    sample_path = tmp_path / 'synopsys_lic01_real.txt'
    license_file_path = tmp_path / 'synopsys_lic01.dat'
    log_path = tmp_path / 'synopsys_lic01.log'

    sample_path.write_text(
        '\n'.join([
            'License server status: 27000@lic01',
            '    License file(s) on lic01: ' + str(license_file_path),
            'lic01: license server UP v11.19',
            'snpslmd: UP v11.19',
            'Users of VCS_MX:  (Total of 10 licenses issued;  Total of 2 licenses in use)',
            '    alice ws01 :0 (vcsd/27000 100) start Tue 3/17 09:00',
            '    bob ws02 :1 (vcsd/27000 101) start Tue 3/17 09:10',
        ]),
        encoding='utf-8',
    )
    license_file_path.write_text(
        '\n'.join([
            'SERVER lic01 001122334455 27000',
            'VENDOR snpslmd /eda/env/license/snpslmd options=/eda/env/license/options.opt',
            'INCREMENT VCS_MX snpslmd 2025.03 31-dec-2026 20 START=15-feb-2024 SN=ABC123 NOTICE="core runtime"',
        ]),
        encoding='utf-8',
    )
    log_path.write_text(
        '\n'.join([
            'TIMESTAMP 03/17/2026',
            '09:15:00 (snpslmd) OUT: "VCS_MX" alice@ws01:0',
            '09:20:12 (snpslmd) DENIED: "VCS_MX" bob@ws02:1 Licensed number of users already reached.',
        ]),
        encoding='utf-8',
    )

    async with session_factory() as session:
        server = LicenseServer(
            name='Synopsys Main',
            vendor='synopsys',
            host='lic01',
            port=27000,
            source_type='sample_file',
            sample_path=str(sample_path),
            license_file_path=str(license_file_path),
            license_log_path=str(log_path),
        )
        session.add(server)
        await session.commit()
        server_id = server.id

    collector = CollectorService()

    async with session_factory() as session:
        result = await collector.collect_single(session, server_id)

        assert result.status == 'up'
        assert result.feature_count == 1

        refreshed_server = await session.get(LicenseServer, server_id)
        assert refreshed_server is not None
        assert refreshed_server.last_status == 'up'
        assert refreshed_server.static_grants_parse_error is None
        assert refreshed_server.log_parse_error is None

        features = (await session.execute(select(LicenseFeature).where(LicenseFeature.server_id == server_id))).scalars().all()
        assert len(features) == 1
        assert features[0].feature_name == 'VCS_MX'
        assert features[0].used_licenses == 2

        asset = (await session.execute(select(LicenseFileAsset).where(LicenseFileAsset.server_id == server_id))).scalar_one()
        assert asset.source_path == str(license_file_path)
        assert asset.server_name == 'lic01'
        assert asset.daemon_name == 'snpslmd'

        grants = (await session.execute(select(StaticLicenseGrant).where(StaticLicenseGrant.server_id == server_id))).scalars().all()
        assert len(grants) == 1
        assert grants[0].feature_name == 'VCS_MX'
        assert grants[0].serial_number == 'ABC123'
        assert grants[0].notice == 'core runtime'

        events = (
            await session.execute(
                select(LicenseLogEvent)
                .where(LicenseLogEvent.server_id == server_id)
                .order_by(LicenseLogEvent.event_time, LicenseLogEvent.id)
            )
        ).scalars().all()
        assert len(events) == 2
        assert [event.event_type for event in events] == ['OUT', 'DENIED']
        assert events[0].event_time is not None
        assert events[0].event_time.year == 2026
        assert events[0].event_time.month == 3
        assert events[0].event_time.day == 17
        assert events[0].event_time.hour == 9
        assert events[0].event_time.minute == 15
        assert events[1].username == 'bob'

    await engine.dispose()


def test_discover_license_file_from_linux_lmstat_output(monkeypatch):
    collector = CollectorService()
    primary = '/eda/env/license/synopsys_lic01.dat'
    secondary = '/eda/env/license/fallback.dat'

    monkeypatch.setattr(
        collector,
        '_normalize_existing_path',
        lambda value: value if value in {primary, secondary} else None,
    )

    raw_text = f'''\nLicense server status: 27000@lic01\n    License file(s) on lic01: {primary}:{secondary}:\n'''

    discovered = collector._discover_license_file_from_lmstat(raw_text)

    assert discovered == primary


@pytest.mark.asyncio
async def test_collect_single_deduplicates_log_events_across_runs(tmp_path):
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    sample_path = tmp_path / 'cadence_lic01_real.txt'
    license_file_path = tmp_path / 'cadence_lic01.dat'
    log_path = tmp_path / 'cadence_lic01.log'

    sample_path.write_text(
        '\n'.join([
            'License server status: 28000@lic01',
            '    License file(s) on lic01: ' + str(license_file_path),
            'lic01: license server UP v11.19',
            'cdslmd: UP v11.19',
            'Users of Virtuoso:  (Total of 5 licenses issued;  Total of 1 licenses in use)',
            '    carol ws03 :0 (virtuoso/28000 200) start Tue 3/17 10:00',
        ]),
        encoding='utf-8',
    )
    license_file_path.write_text(
        '\n'.join([
            'SERVER lic01 aabbccdd0011 28000',
            'VENDOR cdslmd /eda/env/license/cdslmd',
            'FEATURE Virtuoso cdslmd 23.10 31-dec-2026 5 ISSUED=01-jan-2024',
        ]),
        encoding='utf-8',
    )
    log_path.write_text(
        '\n'.join([
            'TIMESTAMP 03/17/2026',
            '10:05:00 (cdslmd) OUT: "Virtuoso" carol@ws03:0',
            '10:06:00 (cdslmd) IN: "Virtuoso" carol@ws03:0',
        ]),
        encoding='utf-8',
    )

    async with session_factory() as session:
        server = LicenseServer(
            name='Cadence Main',
            vendor='cadence',
            host='lic01',
            port=28000,
            source_type='sample_file',
            sample_path=str(sample_path),
            license_file_path=str(license_file_path),
            license_log_path=str(log_path),
        )
        session.add(server)
        await session.commit()
        server_id = server.id

    collector = CollectorService()

    async with session_factory() as session:
        await collector.collect_single(session, server_id)

    async with session_factory() as session:
        await collector.collect_single(session, server_id)
        event_count = (
            await session.execute(select(LicenseLogEvent).where(LicenseLogEvent.server_id == server_id))
        ).scalars().all()
        grant_count = (
            await session.execute(select(StaticLicenseGrant).where(StaticLicenseGrant.server_id == server_id))
        ).scalars().all()

        assert len(event_count) == 2
        assert len(grant_count) == 1

    await engine.dispose()
