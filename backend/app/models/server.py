from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.mixins import TimestampMixin


class LicenseServer(TimestampMixin, Base):
    __tablename__ = 'license_servers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    vendor: Mapped[str] = mapped_column(String(50), nullable=False)
    host: Mapped[str] = mapped_column(String(255), nullable=False)
    port: Mapped[int] = mapped_column(Integer, default=27000, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False)
    source_type: Mapped[str] = mapped_column(String(20), default='lmutil', nullable=False)
    lmutil_path: Mapped[str | None] = mapped_column(String(255), nullable=True)
    lmstat_args: Mapped[str | None] = mapped_column(String(500), nullable=True)
    sample_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_check_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_status: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_error: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    features = relationship('LicenseFeature', back_populates='server', cascade='all, delete-orphan')
