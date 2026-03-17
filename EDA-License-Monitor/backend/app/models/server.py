from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class LicenseServer(TimestampMixin, Base):
    """License server configuration"""
    __tablename__ = 'license_servers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=27000, nullable=False)
    lmutil_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ssh_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ssh_port: Mapped[int] = mapped_column(Integer, default=22, nullable=False)
    ssh_user: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ssh_key_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(20), default='lmutil', nullable=False)
    lmstat_args: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sample_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    license_file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    license_log_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_check_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    static_grants_last_parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    static_grants_parse_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    log_last_parsed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    log_parse_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Relationships (will be populated when Feature model is created)
    features = relationship('LicenseFeature', back_populates='server', cascade='all, delete-orphan', lazy='selectin')
    license_file_asset = relationship('LicenseFileAsset', back_populates='server', cascade='all, delete-orphan', uselist=False, lazy='selectin')
    static_license_grants = relationship('StaticLicenseGrant', back_populates='server', cascade='all, delete-orphan', lazy='selectin')
    log_events = relationship('LicenseLogEvent', back_populates='server', cascade='all, delete-orphan', lazy='selectin')

    def __repr__(self):
        return f"<LicenseServer(id={self.id}, name='{self.name}', vendor='{self.vendor}')>"
