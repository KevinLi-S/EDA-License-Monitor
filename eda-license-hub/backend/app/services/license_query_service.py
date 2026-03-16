from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import Select, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import LicenseCheckout, LicenseFeature, LicenseFileAsset, LicenseLogEvent, StaticLicenseGrant


@dataclass
class FeatureUsageAggregate:
    feature_name: str
    vendor: str
    server_names: set[str] = field(default_factory=set)
    current_users: set[str] = field(default_factory=set)
    current_checkout_count: int = 0
    log_users: set[str] = field(default_factory=set)
    total_log_events: int = 0
    checkout_events: int = 0
    checkin_events: int = 0
    denied_events: int = 0
    last_seen: datetime | None = None


@dataclass
class UserUsageAggregate:
    username: str
    server_names: set[str] = field(default_factory=set)
    feature_names: set[str] = field(default_factory=set)
    current_checkout_count: int = 0
    total_log_events: int = 0
    checkout_events: int = 0
    checkin_events: int = 0
    denied_events: int = 0
    last_seen: datetime | None = None


async def list_license_file_assets(session: AsyncSession, *, server_id: int | None = None) -> list[LicenseFileAsset]:
    stmt: Select[tuple[LicenseFileAsset]] = select(LicenseFileAsset).options(selectinload(LicenseFileAsset.server)).order_by(LicenseFileAsset.id)
    if server_id is not None:
        stmt = stmt.where(LicenseFileAsset.server_id == server_id)
    return (await session.execute(stmt)).scalars().all()


async def list_static_license_grants(
    session: AsyncSession,
    *,
    server_id: int | None = None,
    feature_name: str | None = None,
) -> list[StaticLicenseGrant]:
    stmt: Select[tuple[StaticLicenseGrant]] = (
        select(StaticLicenseGrant)
        .options(selectinload(StaticLicenseGrant.server), selectinload(StaticLicenseGrant.license_file_asset))
        .order_by(StaticLicenseGrant.feature_name, StaticLicenseGrant.id)
    )
    if server_id is not None:
        stmt = stmt.where(StaticLicenseGrant.server_id == server_id)
    if feature_name:
        stmt = stmt.where(StaticLicenseGrant.feature_name == feature_name)
    return (await session.execute(stmt)).scalars().all()


async def list_license_log_events(
    session: AsyncSession,
    *,
    server_id: int | None = None,
    feature_name: str | None = None,
    username: str | None = None,
    limit: int = 200,
) -> list[LicenseLogEvent]:
    stmt: Select[tuple[LicenseLogEvent]] = select(LicenseLogEvent).options(selectinload(LicenseLogEvent.server)).order_by(desc(LicenseLogEvent.event_time), desc(LicenseLogEvent.id))
    if server_id is not None:
        stmt = stmt.where(LicenseLogEvent.server_id == server_id)
    if feature_name:
        stmt = stmt.where(LicenseLogEvent.feature_name == feature_name)
    if username:
        stmt = stmt.where(LicenseLogEvent.username == username)
    stmt = stmt.limit(max(1, min(limit, 1000)))
    return (await session.execute(stmt)).scalars().all()


async def get_feature_usage_aggregates(
    session: AsyncSession,
    *,
    server_id: int | None = None,
    limit: int = 100,
) -> list[FeatureUsageAggregate]:
    aggregates: dict[tuple[str, str], FeatureUsageAggregate] = {}

    feature_stmt: Select[tuple[LicenseFeature]] = select(LicenseFeature).options(selectinload(LicenseFeature.server), selectinload(LicenseFeature.checkouts))
    if server_id is not None:
        feature_stmt = feature_stmt.where(LicenseFeature.server_id == server_id)
    features = (await session.execute(feature_stmt)).scalars().all()

    for feature in features:
        vendor = feature.vendor or (feature.server.vendor if feature.server else 'unknown')
        key = (feature.feature_name, vendor)
        aggregate = aggregates.setdefault(key, FeatureUsageAggregate(feature_name=feature.feature_name, vendor=vendor))
        if feature.server:
            aggregate.server_names.add(feature.server.name)
        active_checkouts = [checkout for checkout in feature.checkouts if checkout.is_active]
        aggregate.current_checkout_count += len(active_checkouts)
        aggregate.current_users.update(checkout.username for checkout in active_checkouts if checkout.username)
        for checkout in active_checkouts:
            if checkout.checkout_time and (aggregate.last_seen is None or checkout.checkout_time > aggregate.last_seen):
                aggregate.last_seen = checkout.checkout_time

    log_stmt: Select[tuple[LicenseLogEvent]] = select(LicenseLogEvent).options(selectinload(LicenseLogEvent.server))
    if server_id is not None:
        log_stmt = log_stmt.where(LicenseLogEvent.server_id == server_id)
    events = (await session.execute(log_stmt)).scalars().all()

    for event in events:
        if not event.feature_name:
            continue
        vendor = event.server.vendor if event.server else (event.vendor_daemon or 'unknown')
        key = (event.feature_name, vendor)
        aggregate = aggregates.setdefault(key, FeatureUsageAggregate(feature_name=event.feature_name, vendor=vendor))
        if event.server:
            aggregate.server_names.add(event.server.name)
        if event.username:
            aggregate.log_users.add(event.username)
        aggregate.total_log_events += 1
        if event.event_type == 'OUT':
            aggregate.checkout_events += 1
        elif event.event_type == 'IN':
            aggregate.checkin_events += 1
        elif event.event_type == 'DENIED':
            aggregate.denied_events += 1
        if event.event_time and (aggregate.last_seen is None or event.event_time > aggregate.last_seen):
            aggregate.last_seen = event.event_time

    rows = sorted(
        aggregates.values(),
        key=lambda item: (-item.current_checkout_count, -item.total_log_events, item.feature_name.lower(), item.vendor.lower()),
    )
    return rows[: max(1, min(limit, 500))]


async def get_user_usage_ranking(
    session: AsyncSession,
    *,
    server_id: int | None = None,
    limit: int = 100,
) -> list[UserUsageAggregate]:
    aggregates: dict[str, UserUsageAggregate] = {}

    checkout_stmt: Select[tuple[LicenseCheckout]] = (
        select(LicenseCheckout)
        .options(selectinload(LicenseCheckout.feature).selectinload(LicenseFeature.server))
        .where(LicenseCheckout.is_active.is_(True))
    )
    if server_id is not None:
        checkout_stmt = checkout_stmt.join(LicenseCheckout.feature).where(LicenseFeature.server_id == server_id)
    checkouts = (await session.execute(checkout_stmt)).scalars().all()

    for checkout in checkouts:
        username = checkout.username or 'unknown'
        aggregate = aggregates.setdefault(username, UserUsageAggregate(username=username))
        aggregate.current_checkout_count += 1
        if checkout.feature:
            aggregate.feature_names.add(checkout.feature.feature_name)
            if checkout.feature.server:
                aggregate.server_names.add(checkout.feature.server.name)
        if checkout.checkout_time and (aggregate.last_seen is None or checkout.checkout_time > aggregate.last_seen):
            aggregate.last_seen = checkout.checkout_time

    event_stmt: Select[tuple[LicenseLogEvent]] = select(LicenseLogEvent).options(selectinload(LicenseLogEvent.server))
    if server_id is not None:
        event_stmt = event_stmt.where(LicenseLogEvent.server_id == server_id)
    events = (await session.execute(event_stmt)).scalars().all()

    for event in events:
        if not event.username:
            continue
        aggregate = aggregates.setdefault(event.username, UserUsageAggregate(username=event.username))
        aggregate.total_log_events += 1
        if event.feature_name:
            aggregate.feature_names.add(event.feature_name)
        if event.server:
            aggregate.server_names.add(event.server.name)
        if event.event_type == 'OUT':
            aggregate.checkout_events += 1
        elif event.event_type == 'IN':
            aggregate.checkin_events += 1
        elif event.event_type == 'DENIED':
            aggregate.denied_events += 1
        if event.event_time and (aggregate.last_seen is None or event.event_time > aggregate.last_seen):
            aggregate.last_seen = event.event_time

    rows = sorted(
        aggregates.values(),
        key=lambda item: (-item.current_checkout_count, -item.checkout_events, -item.total_log_events, item.username.lower()),
    )
    return rows[: max(1, min(limit, 500))]
