from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class LicenseFeature(TimestampMixin, Base):
    __tablename__ = 'license_features'
    __table_args__ = (UniqueConstraint('server_id', 'feature_name', name='uq_server_feature_name'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    server_id: Mapped[int] = mapped_column(ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False)
    feature_name: Mapped[str] = mapped_column(String(100), nullable=False)
    total_licenses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    used_licenses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_licenses: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    usage_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)
    vendor: Mapped[str | None] = mapped_column(String(50), nullable=True)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    raw_block: Mapped[str | None] = mapped_column(String, nullable=True)

    server = relationship('LicenseServer', back_populates='features')
    usage_history = relationship('LicenseUsageHistory', back_populates='feature', cascade='all, delete-orphan')
    checkouts = relationship('LicenseCheckout', back_populates='feature', cascade='all, delete-orphan')


class LicenseUsageHistory(Base):
    __tablename__ = 'license_usage_history'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feature_id: Mapped[int] = mapped_column(ForeignKey('license_features.id', ondelete='CASCADE'), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    available_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    usage_percentage: Mapped[float] = mapped_column(Numeric(5, 2), default=0, nullable=False)

    feature = relationship('LicenseFeature', back_populates='usage_history')
