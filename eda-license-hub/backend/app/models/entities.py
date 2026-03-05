from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)


class LicenseServer(Base):
    __tablename__ = "license_servers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"))
    name: Mapped[str] = mapped_column(String(128), index=True)
    host: Mapped[str] = mapped_column(String(128))
    port: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(32), default="unknown")
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Feature(Base):
    __tablename__ = "features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor_id: Mapped[int] = mapped_column(ForeignKey("vendors.id"))
    name: Mapped[str] = mapped_column(String(128), index=True)


class FeatureSnapshot(Base):
    __tablename__ = "feature_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("license_servers.id"))
    feature_id: Mapped[int] = mapped_column(ForeignKey("features.id"))
    total: Mapped[int] = mapped_column(Integer)
    used: Mapped[int] = mapped_column(Integer)
    free: Mapped[int] = mapped_column(Integer)
    collected_at: Mapped[datetime] = mapped_column(DateTime, index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    type: Mapped[str] = mapped_column(String(64), index=True)
    severity: Mapped[str] = mapped_column(String(16), default="medium")
    server_id: Mapped[int | None] = mapped_column(ForeignKey("license_servers.id"), nullable=True)
    feature_id: Mapped[int | None] = mapped_column(ForeignKey("features.id"), nullable=True)
    message: Mapped[str] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32), default="open")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ServerActionLog(Base):
    __tablename__ = "server_action_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    server_id: Mapped[int] = mapped_column(ForeignKey("license_servers.id"))
    action: Mapped[str] = mapped_column(String(32), index=True)
    status_after: Mapped[str] = mapped_column(String(32))
    message: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LicenseKeyRecord(Base):
    __tablename__ = "license_key_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    vendor: Mapped[str] = mapped_column(String(64), index=True)
    feature: Mapped[str] = mapped_column(String(128), index=True)
    version: Mapped[str] = mapped_column(String(64), default="N/A")
    total: Mapped[int] = mapped_column(Integer, default=0)
    used: Mapped[int] = mapped_column(Integer, default=0)
    expiry: Mapped[str] = mapped_column(String(32), default="N/A")
    server: Mapped[str] = mapped_column(String(128), default="unknown")
    source_file: Mapped[str] = mapped_column(String(256), default="")
    collected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
