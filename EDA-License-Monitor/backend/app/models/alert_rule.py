"""Alert Rule model"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base


class AlertRule(Base):
    """Alert rules configuration table"""

    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="Rule name")
    rule_type = Column(String(50), nullable=False, index=True, comment="usage_threshold/server_down")
    target_type = Column(String(50), comment="server/feature")
    target_id = Column(Integer, comment="Target ID (server_id or feature_id)")
    threshold_value = Column(Numeric(5, 2), comment="Threshold (e.g., 90 = 90%)")
    notification_channels = Column(JSONB, comment="Notification channels config")
    enabled = Column(Boolean, default=True, index=True, comment="Is enabled")
    cooldown_minutes = Column(Integer, default=5, comment="Cooldown time in minutes")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.name}', type='{self.rule_type}')>"
