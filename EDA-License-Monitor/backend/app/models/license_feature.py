"""License Feature model"""
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import backref, relationship
from app.database import Base


class LicenseFeature(Base):
    """License feature table"""

    __tablename__ = "license_features"

    id = Column(Integer, primary_key=True, index=True)
    server_id = Column(Integer, ForeignKey("license_servers.id", ondelete="CASCADE"), nullable=False)
    feature_name = Column(String(100), nullable=False, comment="Feature name, e.g. 'VCS_Runtime'")
    total_licenses = Column(Integer, nullable=False, comment="Total authorized licenses")
    vendor = Column(String(50), comment="Vendor")
    version = Column(String(50), comment="Version")
    expiry_date = Column(Date, index=True, comment="Expiration date")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    server = relationship(
        "LicenseServer",
        backref=backref("features", lazy="selectin"),
        lazy="selectin",
    )

    # Unique constraint
    __table_args__ = (
        UniqueConstraint('server_id', 'feature_name', name='idx_server_feature'),
    )

    def __repr__(self):
        return f"<LicenseFeature(id={self.id}, name='{self.feature_name}', total={self.total_licenses})>"
