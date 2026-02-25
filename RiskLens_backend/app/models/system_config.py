from sqlalchemy import Column, Integer, Boolean
from app.core.database import Base

class SystemConfig(Base):
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True)

    auto_scan_enabled = Column(Boolean, default=True)
    scan_interval_minutes = Column(Integer, default=5)