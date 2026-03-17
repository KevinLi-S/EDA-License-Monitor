"""License Usage History model"""
from sqlalchemy import Column, BigInteger, Integer, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.database import Base


class LicenseUsageHistory(Base):
    """License usage history table (time-series data)"""

    __tablename__ = "license_usage_history"

    id = Column(BigInteger, primary_key=True, index=True)
    feature_id = Column(Integer, ForeignKey("license_features.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    used_count = Column(Integer, nullable=False, comment="Used count")
    available_count = Column(Integer, nullable=False, comment="Available count")
    usage_percentage = Column(Numeric(5, 2), comment="Usage percentage")
    queued_count = Column(Integer, default=0, comment="Queued count")

    # Relationships
    feature = relationship("LicenseFeature", backref="usage_history")

    # Composite index for trend queries
    __table_args__ = (
        Index('idx_feature_timestamp', 'feature_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<LicenseUsageHistory(feature_id={self.feature_id}, used={self.used_count}, timestamp={self.timestamp})>"
