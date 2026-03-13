from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class LicenseCheckout(Base):
    __tablename__ = 'license_checkouts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    feature_id: Mapped[int] = mapped_column(ForeignKey('license_features.id', ondelete='CASCADE'), nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    hostname: Mapped[str] = mapped_column(String(255), nullable=False)
    display: Mapped[str | None] = mapped_column(String(100), nullable=True)
    process_info: Mapped[str | None] = mapped_column(Text, nullable=True)
    checkout_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    server_handle: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    feature = relationship('LicenseFeature', back_populates='checkouts')
