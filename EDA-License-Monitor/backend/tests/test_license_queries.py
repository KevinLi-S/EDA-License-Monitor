from datetime import UTC, datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_session
from app.main import app
from app.models import LicenseCheckout, LicenseFeature, LicenseFileAsset, LicenseLogEvent, LicenseServer, StaticLicenseGrant


@pytest.mark.asyncio
async def test_license_query_endpoints():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:', echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_session():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    try:
        async with session_factory() as session:
            server = LicenseServer(name='Synopsys Main', vendor='synopsys', host='lic01', port=27000)
            session.add(server)
            await session.flush()

            feature = LicenseFeature(
                server_id=server.id,
                feature_name='VCS_MX',
                vendor='synopsys',
                version='2025.03',
                total_licenses=10,
                used_licenses=2,
                available_licenses=8,
                usage_percentage=20,
            )
            session.add(feature)
            await session.flush()

            session.add(LicenseCheckout(
                feature_id=feature.id,
                username='alice',
                hostname='ws01',
                display=':0',
                process_info='alice ws01 :0 (vcsd/27000 100)',
                checkout_time=datetime(2026, 3, 16, 10, 0, tzinfo=UTC),
                server_handle='vcsd/27000 100',
                is_active=True,
            ))

            asset = LicenseFileAsset(
                server_id=server.id,
                source_path='/eda/env/license/synopsys_lic01.dat',
                server_name='lic01',
                server_hostid='abc123',
                server_port='27000',
                daemon_name='snpslmd',
                daemon_path='/eda/env/license/snpslmd',
                options_path='/eda/env/license/options.opt',
                raw_header='SERVER lic01 abc123 27000',
                last_parsed_at=datetime(2026, 3, 16, 11, 0, tzinfo=UTC),
            )
            session.add(asset)
            await session.flush()

            session.add_all([
                StaticLicenseGrant(
                    server_id=server.id,
                    license_file_asset_id=asset.id,
                    record_type='INCREMENT',
                    vendor_name='snpslmd',
                    feature_name='VCS_MX',
                    version='2025.03',
                    quantity=20,
                    serial_number='S123',
                    raw_record='INCREMENT VCS_MX snpslmd 2025.03 31-dec-2026 20',
                ),
                StaticLicenseGrant(
                    server_id=server.id,
                    license_file_asset_id=asset.id,
                    record_type='FEATURE',
                    vendor_name='otherd',
                    feature_name='TEMP_FEATURE',
                    version='1.0',
                    quantity=5,
                    serial_number='S999',
                    raw_record='FEATURE TEMP_FEATURE otherd 1.0 31-dec-2026 5',
                ),
            ])

            session.add_all([
                LicenseLogEvent(
                    server_id=server.id,
                    event_type='OUT',
                    event_time=datetime(2026, 3, 16, 10, 5, tzinfo=UTC),
                    vendor_daemon='snpslmd',
                    feature_name='VCS_MX',
                    username='alice',
                    hostname='ws01',
                    display=':0',
                    event_hash='hash-out',
                    raw_line='10:05:00 (snpslmd) OUT: "VCS_MX" alice@ws01:0',
                ),
                LicenseLogEvent(
                    server_id=server.id,
                    event_type='DENIED',
                    event_time=datetime(2026, 3, 16, 10, 6, tzinfo=UTC),
                    vendor_daemon='snpslmd',
                    feature_name='VCS_MX',
                    username='bob',
                    hostname='ws02',
                    display=':0',
                    event_hash='hash-denied',
                    raw_line='10:06:00 (snpslmd) DENIED: "VCS_MX" bob@ws02:0',
                ),
                LicenseLogEvent(
                    server_id=server.id,
                    event_type='OUT',
                    event_time=datetime(2026, 3, 16, 10, 7, tzinfo=UTC),
                    vendor_daemon='otherd',
                    feature_name='TEMP_FEATURE',
                    username='charlie',
                    hostname='ws03',
                    display=':1',
                    event_hash='hash-out-other',
                    raw_line='10:07:00 (otherd) OUT: "TEMP_FEATURE" charlie@ws03:1',
                ),
            ])
            await session.commit()

        async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
            asset_resp = await client.get('/api/v1/licenses/file-assets')
            grants_resp = await client.get('/api/v1/licenses/static-grants', params={'feature_name': 'VCS_MX'})
            grants_filtered_resp = await client.get('/api/v1/licenses/static-grants', params={'vendor_name': 'snpslmd', 'record_type': 'INCREMENT'})
            events_resp = await client.get('/api/v1/licenses/log-events', params={'limit': 10})
            events_filtered_resp = await client.get('/api/v1/licenses/log-events', params={'event_type': 'DENIED', 'vendor_daemon': 'snpslmd', 'limit': 10})
            feature_usage_resp = await client.get('/api/v1/licenses/feature-usage')
            feature_usage_time_resp = await client.get('/api/v1/licenses/feature-usage', params={'start_time': '2026-03-16T10:06:00Z', 'end_time': '2026-03-16T10:06:00Z'})
            usage_time_resp = await client.get('/api/v1/licenses/usage', params={'start_time': '2026-03-16T10:00:00Z', 'end_time': '2026-03-16T10:00:00Z'})
            user_ranking_resp = await client.get('/api/v1/licenses/user-ranking')
            user_ranking_time_resp = await client.get('/api/v1/licenses/user-ranking', params={'start_time': '2026-03-16T10:06:00Z', 'end_time': '2026-03-16T10:06:00Z'})

        assert asset_resp.status_code == 200
        assert grants_resp.status_code == 200
        assert grants_filtered_resp.status_code == 200
        assert events_resp.status_code == 200
        assert events_filtered_resp.status_code == 200
        assert feature_usage_resp.status_code == 200
        assert feature_usage_time_resp.status_code == 200
        assert usage_time_resp.status_code == 200
        assert user_ranking_resp.status_code == 200
        assert user_ranking_time_resp.status_code == 200

        asset_rows = asset_resp.json()
        grant_rows = grants_resp.json()
        filtered_grant_rows = grants_filtered_resp.json()
        event_rows = events_resp.json()
        filtered_event_rows = events_filtered_resp.json()
        feature_usage_rows = feature_usage_resp.json()
        feature_usage_time_rows = feature_usage_time_resp.json()
        usage_time_rows = usage_time_resp.json()
        ranking_rows = user_ranking_resp.json()
        ranking_time_rows = user_ranking_time_resp.json()

        assert asset_rows[0]['source_path'] == '/eda/env/license/synopsys_lic01.dat'
        assert grant_rows[0]['feature_name'] == 'VCS_MX'
        assert filtered_grant_rows == [grant_rows[0]]
        assert event_rows[0]['event_type'] == 'OUT'
        assert filtered_event_rows[0]['event_type'] == 'DENIED'
        assert filtered_event_rows[0]['vendor_daemon'] == 'snpslmd'
        assert feature_usage_rows[0]['feature_name'] == 'VCS_MX'
        assert feature_usage_rows[0]['current_users'] == ['alice']
        assert feature_usage_rows[0]['log_users'] == ['alice', 'bob']
        assert feature_usage_rows[0]['unique_user_count'] == 2
        assert feature_usage_rows[0]['denied_events'] == 1
        assert feature_usage_time_rows[0]['feature_name'] == 'VCS_MX'
        assert feature_usage_time_rows[0]['current_checkout_count'] == 0
        assert feature_usage_time_rows[0]['denied_events'] == 1
        assert usage_time_rows[0]['username'] == 'alice'
        assert ranking_rows[0]['username'] == 'alice'
        assert ranking_rows[0]['current_checkout_count'] == 1
        assert ranking_rows[0]['feature_names'] == ['VCS_MX']
        assert ranking_time_rows[0]['username'] == 'bob'
        assert ranking_time_rows[0]['current_checkout_count'] == 0
        assert ranking_time_rows[0]['denied_events'] == 1
    finally:
        app.dependency_overrides.pop(get_session, None)
        await engine.dispose()
