"""Alert Log model"""
from sqlalchemy import Column, BigInteger, Integer, String, Text, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class AlertLog(Base):
    """Alert logs table"""

    __tablename__ = "alert_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("alert_rules.id", ondelete="CASCADE"), nullable=False)
    triggered_at = Column(DateTime(timezone=True), nullable=False, comment="Trigger time")
    severity = Column(String(20), nullable=False, comment="warning/critical")
    message = Column(Text, nullable=False, comment="Alert message")
    context_data = Column(JSONB, comment="Context data")
    resolved_at = Column(DateTime(timezone=True), index=True, comment="Resolved time")
    notified = Column(Boolean, default=False, comment="Has been notified")
    notification_status = Column(JSONB, comment="Notification results")

    # Relationships
    rule = relationship("AlertRule", backref="logs")

    # Composite index
    __table_args__ = (
        Index('idx_rule_triggered', 'rule_id', 'triggered_at'),
    )

    def __repr__(self):
        return f"<AlertLog(id={self.id}, severity='{self.severity}', message='{self.message[:50]}')>"
