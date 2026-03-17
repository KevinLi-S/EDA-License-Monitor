"""Audit Log model"""
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from app.database import Base


class AuditLog(Base):
    """Audit logs table"""

    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("admin_users.id", ondelete="SET NULL"), comment="User ID")
    action = Column(String(100), nullable=False, index=True, comment="Action type")
    resource_type = Column(String(50), comment="Resource type")
    resource_id = Column(Integer, comment="Resource ID")
    details = Column(JSONB, comment="Operation details")
    ip_address = Column(String(50), comment="IP address")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), comment="Operation time")

    # Relationships
    user = relationship("AdminUser", backref="audit_logs")

    # Composite index
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', user_id={self.user_id})>"
