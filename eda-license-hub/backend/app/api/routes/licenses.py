from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import LicenseCheckout, LicenseFeature


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.replace(tzinfo=None) if value.tzinfo is not None else value
from app.schemas.license import (
    FeatureUsageAggregateSummary,
    LicenseFileAssetSummary,
    LicenseKeySummary,
    LicenseLogEventSummary,
    LicenseUsageSummary,
    StaticLicenseGrantSummary,
    UserUsageRankingSummary,
)
from app.services.license_query_service import (
    get_feature_usage_aggregates,
    get_user_usage_ranking,
    list_license_file_assets,
    list_license_log_events,
    list_static_license_grants,
)

router = APIRouter()


@router.get('/keys', response_model=list[LicenseKeySummary])
async def get_license_keys(session: AsyncSession = Depends(get_session)) -> list[LicenseKeySummary]:
    stmt = (
        select(LicenseFeature)
        .options(selectinload(LicenseFeature.server))
        .order_by(LicenseFeature.vendor, LicenseFeature.feature_name)
    )
    features = (await session.execute(stmt)).scalars().all()
    return [
        LicenseKeySummary(
            id=feature.id,
            key_name=feature.feature_name,
            vendor=feature.vendor or (feature.server.vendor if feature.server else 'unknown'),
            version=feature.version,
            server_name=feature.server.name if feature.server else 'unknown',
            issued=feature.total_licenses,
            used=feature.used_licenses,
            available=feature.available_licenses,
            usage_percent=float(feature.usage_percentage or 0),
        )
        for feature in features
    ]


@router.get('/usage', response_model=list[LicenseUsageSummary])
async def get_license_usage(
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[LicenseUsageSummary]:
    start_time = _normalize_datetime(start_time)
    end_time = _normalize_datetime(end_time)

    stmt = (
        select(LicenseCheckout)
        .options(
            selectinload(LicenseCheckout.feature).selectinload(LicenseFeature.server)
        )
        .where(LicenseCheckout.is_active.is_(True))
        .order_by(LicenseCheckout.checkout_time.desc())
    )
    if start_time is not None:
        stmt = stmt.where(LicenseCheckout.checkout_time >= start_time)
    if end_time is not None:
        stmt = stmt.where(LicenseCheckout.checkout_time <= end_time)
    checkouts = (await session.execute(stmt)).scalars().all()
    return [
        LicenseUsageSummary(
            id=checkout.id,
            key_name=checkout.feature.feature_name,
            vendor=checkout.feature.vendor or (checkout.feature.server.vendor if checkout.feature.server else 'unknown'),
            version=checkout.feature.version,
            username=checkout.username,
            client_hostname=checkout.hostname,
            last_used=checkout.checkout_time.isoformat(),
            server_name=checkout.feature.server.name if checkout.feature.server else 'unknown',
        )
        for checkout in checkouts
    ]


@router.get('/file-assets', response_model=list[LicenseFileAssetSummary])
async def get_license_file_assets(
    server_id: int | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[LicenseFileAssetSummary]:
    assets = await list_license_file_assets(session, server_id=server_id)
    return [
        LicenseFileAssetSummary(
            id=asset.id,
            server_id=asset.server_id,
            server_label=asset.server.name if asset.server else 'unknown',
            server_name=asset.server_name,
            server_hostid=asset.server_hostid,
            server_port=asset.server_port,
            daemon_name=asset.daemon_name,
            daemon_path=asset.daemon_path,
            options_path=asset.options_path,
            source_path=asset.source_path,
            raw_header=asset.raw_header,
            last_parsed_at=asset.last_parsed_at,
        )
        for asset in assets
    ]


@router.get('/static-grants', response_model=list[StaticLicenseGrantSummary])
async def get_static_license_grants(
    server_id: int | None = Query(default=None),
    feature_name: str | None = Query(default=None),
    vendor_name: str | None = Query(default=None),
    record_type: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
) -> list[StaticLicenseGrantSummary]:
    grants = await list_static_license_grants(
        session,
        server_id=server_id,
        feature_name=feature_name,
        vendor_name=vendor_name,
        record_type=record_type,
    )
    return [
        StaticLicenseGrantSummary(
            id=grant.id,
            server_id=grant.server_id,
            server_label=grant.server.name if grant.server else 'unknown',
            license_file_asset_id=grant.license_file_asset_id,
            feature_name=grant.feature_name,
            vendor_name=grant.vendor_name,
            record_type=grant.record_type,
            version=grant.version,
            quantity=grant.quantity,
            issued_date=grant.issued_date,
            start_date=grant.start_date,
            expiry_date=grant.expiry_date,
            expiry_text=grant.expiry_text,
            serial_number=grant.serial_number,
            notice=grant.notice,
        )
        for grant in grants
    ]


@router.get('/log-events', response_model=list[LicenseLogEventSummary])
async def get_log_events(
    server_id: int | None = Query(default=None),
    feature_name: str | None = Query(default=None),
    username: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    vendor_daemon: str | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
) -> list[LicenseLogEventSummary]:
    events = await list_license_log_events(
        session,
        server_id=server_id,
        feature_name=feature_name,
        username=username,
        event_type=event_type,
        vendor_daemon=vendor_daemon,
        start_time=start_time,
        end_time=end_time,
        limit=limit,
    )
    return [
        LicenseLogEventSummary(
            id=event.id,
            server_id=event.server_id,
            server_label=event.server.name if event.server else 'unknown',
            event_type=event.event_type,
            event_time=event.event_time,
            vendor_daemon=event.vendor_daemon,
            feature_name=event.feature_name,
            username=event.username,
            hostname=event.hostname,
            display=event.display,
            raw_line=event.raw_line,
        )
        for event in events
    ]


@router.get('/feature-usage', response_model=list[FeatureUsageAggregateSummary])
async def get_feature_usage(
    server_id: int | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[FeatureUsageAggregateSummary]:
    rows = await get_feature_usage_aggregates(session, server_id=server_id, start_time=start_time, end_time=end_time, limit=limit)
    return [
        FeatureUsageAggregateSummary(
            feature_name=row.feature_name,
            vendor=row.vendor,
            server_names=sorted(row.server_names),
            current_users=sorted(row.current_users),
            current_checkout_count=row.current_checkout_count,
            log_users=sorted(row.log_users),
            unique_user_count=len(row.current_users | row.log_users),
            total_log_events=row.total_log_events,
            checkout_events=row.checkout_events,
            checkin_events=row.checkin_events,
            denied_events=row.denied_events,
            last_seen=row.last_seen,
        )
        for row in rows
    ]


@router.get('/user-ranking', response_model=list[UserUsageRankingSummary])
async def get_user_ranking(
    server_id: int | None = Query(default=None),
    start_time: datetime | None = Query(default=None),
    end_time: datetime | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
) -> list[UserUsageRankingSummary]:
    rows = await get_user_usage_ranking(session, server_id=server_id, start_time=start_time, end_time=end_time, limit=limit)
    return [
        UserUsageRankingSummary(
            username=row.username,
            server_names=sorted(row.server_names),
            feature_names=sorted(row.feature_names),
            unique_feature_count=len(row.feature_names),
            current_checkout_count=row.current_checkout_count,
            total_log_events=row.total_log_events,
            checkout_events=row.checkout_events,
            checkin_events=row.checkin_events,
            denied_events=row.denied_events,
            last_seen=row.last_seen,
        )
        for row in rows
    ]
