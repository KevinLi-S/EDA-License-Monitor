from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class LicenseLogEvent(TimestampMixin, Base):
    __tablename__ = 'license_log_events'
    __table_args__ = (UniqueConstraint('event_hash', name='uq_license_log_event_hash'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    server_id: Mapped[int] = mapped_column(ForeignKey('license_servers.id', ondelete='CASCADE'), nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    event_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    vendor_daemon: Mapped[str | None] = mapped_column(String(100), nullable=True)
    feature_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hostname: Mapped[str | None] = mapped_column(String(255), nullable=True)
    display: Mapped[str | None] = mapped_column(String(100), nullable=True)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    raw_line: Mapped[str] = mapped_column(Text, nullable=False)

    server = relationship('LicenseServer', back_populates='log_events')
