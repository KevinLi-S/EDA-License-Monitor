"""License Server model"""
from sqlalchemy import Column, Integer, String, DateTime, func
from app.database import Base


class LicenseServer(Base):
    """License server configuration table"""

    __tablename__ = "license_servers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="Server name, e.g. 'Synopsys Main'")
    vendor = Column(String(50), nullable=False, index=True, comment="Vendor: synopsys/cadence/mentor/ansys")
    host = Column(String(255), nullable=False, comment="Server address")
    port = Column(Integer, default=27000, comment="License port")
    lmutil_path = Column(String(255), comment="lmutil tool path")
    ssh_host = Column(String(255), comment="SSH management address")
    ssh_port = Column(Integer, default=22, comment="SSH port")
    ssh_user = Column(String(50), comment="SSH username")
    ssh_key_path = Column(String(255), comment="SSH key path")
    status = Column(String(20), default='active', index=True, comment="active/inactive")
    last_check_time = Column(DateTime(timezone=True), comment="Last check time")
    last_status = Column(String(20), comment="up/down")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Created time")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Updated time")

    def __repr__(self):
        return f"<LicenseServer(id={self.id}, name='{self.name}', vendor='{self.vendor}')>"
