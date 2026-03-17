from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LicenseFeature, LicenseServer, LicenseUsageHistory
from app.schemas.alert import AlertSummary
from app.schemas.analytics import UsageTrendPoint
from app.schemas.dashboard import DashboardKpi, DashboardOverview
from app.schemas.server import ServerSummary


async def list_servers(session: AsyncSession) -> list[ServerSummary]:
    feature_count_subq = (
        select(LicenseFeature.server_id, func.count(LicenseFeature.id).label('feature_count'), func.max(LicenseFeature.usage_percentage).label('usage_percent'))
        .group_by(LicenseFeature.server_id)
        .subquery()
    )
    stmt = (
        select(
            LicenseServer.id,
            LicenseServer.name,
            LicenseServer.vendor,
            LicenseServer.host,
            LicenseServer.port,
            LicenseServer.last_status,
            func.coalesce(feature_count_subq.c.feature_count, 0),
            func.coalesce(feature_count_subq.c.usage_percent, 0),
        )
        .outerjoin(feature_count_subq, feature_count_subq.c.server_id == LicenseServer.id)
        .order_by(LicenseServer.id)
    )
    rows = (await session.execute(stmt)).all()
    return [
        ServerSummary(
            id=row[0],
            name=row[1],
            vendor=row[2],
            host=row[3],
            port=row[4],
            status=row[5] or 'unknown',
            feature_count=int(row[6] or 0),
            usage_percent=float(row[7] or 0),
        )
        for row in rows
    ]


async def list_alerts(session: AsyncSession) -> list[AlertSummary]:
    stmt = select(LicenseServer).where(
        LicenseServer.last_status == 'down',
        LicenseServer.vendor.not_in(['synopsys', 'cadence', 'mentor', 'ansys'])
    ).order_by(LicenseServer.id)
    servers = (await session.execute(stmt)).scalars().all()
    now = datetime.now(UTC)
    return [
        AlertSummary(
            id=server.id,
            severity='critical',
            message=f'{server.name} collector failed: {server.last_error or "server down"}',
            triggered_at=server.last_check_time or now,
            source='collector',
        )
        for server in servers[:10]
    ]


async def get_usage_trend(session: AsyncSession) -> list[UsageTrendPoint]:
    since = datetime.now(UTC) - timedelta(hours=8)
    stmt = (
        select(LicenseUsageHistory.timestamp, func.avg(LicenseUsageHistory.usage_percentage))
        .where(LicenseUsageHistory.timestamp >= since)
        .group_by(LicenseUsageHistory.timestamp)
        .order_by(LicenseUsageHistory.timestamp)
    )
    rows = (await session.execute(stmt)).all()
    return [UsageTrendPoint(timestamp=row[0], usage_percent=float(row[1] or 0)) for row in rows]


async def get_dashboard_overview(session: AsyncSession) -> DashboardOverview:
    servers = await list_servers(session)
    alerts = await list_alerts(session)

    total_servers = len(servers)
    online_servers = sum(1 for server in servers if server.status == 'up')
    total_features = sum(server.feature_count for server in servers)
    peak_usage = max((server.usage_percent for server in servers), default=0)

    last_collection_stmt = select(func.max(LicenseServer.last_check_time))
    last_collection = (await session.execute(last_collection_stmt)).scalar_one_or_none()

    kpis = [
        DashboardKpi(label='Active servers', value=f'{online_servers} / {total_servers}', trend='collector-backed'),
        DashboardKpi(label='Critical alerts', value=str(len(alerts)), trend='collector failures only'),
        DashboardKpi(label='Peak utilization', value=f'{peak_usage:.1f}%', trend='max feature usage across servers'),
        DashboardKpi(label='Tracked features', value=str(total_features), trend=f'last collect: {last_collection.isoformat() if last_collection else "never"}'),
    ]
    return DashboardOverview(kpis=kpis, servers=servers, alerts=alerts)
