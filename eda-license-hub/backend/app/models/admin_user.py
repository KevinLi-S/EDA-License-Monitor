"""Admin User model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from app.database import Base


class AdminUser(Base):
    """Admin users table"""

    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, unique=True, index=True, comment="Username")
    password_hash = Column(String(255), nullable=False, comment="bcrypt password hash")
    email = Column(String(100), comment="Email")
    is_active = Column(Boolean, default=True, comment="Is active")
    last_login = Column(DateTime(timezone=True), comment="Last login time")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}')>"
