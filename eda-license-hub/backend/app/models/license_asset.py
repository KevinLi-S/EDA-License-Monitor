from __future__ import annotations

from datetime import datetime, date

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class LicenseFileAsset(TimestampMixin, Base):
    __tablename__ = 'license_file_assets'
    __table_args__ = (UniqueConstraint('server_id', name='uq_license_file_asset_server'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    server_id: Mapped[int] = mapped_column(ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False)
    source_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    server_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    server_hostid: Mapped[str | None] = mapped_column(String(255), nullable=True)
    server_port: Mapped[str | None] = mapped_column(String(50), nullable=True)
    daemon_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    daemon_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    options_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    raw_header: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_parsed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    server = relationship('LicenseServer', back_populates='license_file_asset')
    grants = relationship('StaticLicenseGrant', back_populates='license_file_asset', cascade='all, delete-orphan')


class StaticLicenseGrant(TimestampMixin, Base):
    __tablename__ = 'static_license_grants'
    __table_args__ = (
        UniqueConstraint(
            'server_id',
            'feature_name',
            'record_type',
            'version',
            'expiry_date',
            'serial_number',
            name='uq_static_license_grant_identity',
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    server_id: Mapped[int] = mapped_column(ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False)
    license_file_asset_id: Mapped[int | None] = mapped_column(ForeignKey('license_file_assets.id', ondelete='CASCADE'), nullable=True)
    record_type: Mapped[str] = mapped_column(String(20), nullable=False)
    vendor_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    feature_name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    issued_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_text: Mapped[str | None] = mapped_column(String(50), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notice: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_record: Mapped[str] = mapped_column(Text, nullable=False)

    server = relationship('LicenseServer', back_populates='static_license_grants')
    license_file_asset = relationship('LicenseFileAsset', back_populates='grants')
