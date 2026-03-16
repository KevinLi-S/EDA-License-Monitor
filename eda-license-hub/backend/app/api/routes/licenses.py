from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_session
from app.models import LicenseCheckout, LicenseFeature
from app.schemas.license import LicenseKeySummary, LicenseUsageSummary

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
async def get_license_usage(session: AsyncSession = Depends(get_session)) -> list[LicenseUsageSummary]:
    stmt = (
        select(LicenseCheckout)
        .options(
            selectinload(LicenseCheckout.feature).selectinload(LicenseFeature.server)
        )
        .where(LicenseCheckout.is_active.is_(True))
        .order_by(LicenseCheckout.checkout_time.desc())
    )
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
