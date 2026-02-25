from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class ScanHistory(Base):
    __tablename__ = "scan_history"

    id = Column(Integer, primary_key=True, index=True)

    target_db_id = Column(Integer, ForeignKey("target_databases.id"), nullable=True)

    scan_mode = Column(String, nullable=False)  # database / file
    input_format = Column(String, nullable=True)  # csv, json, xlsx, sql, xml
    file_name = Column(String, nullable=True)

    total_rules = Column(Integer)
    violations = relationship("Violation", back_populates="scan",cascade="all, delete-orphan")
    total_violations = Column(Integer)

    status = Column(String, default="Completed")
    duration_seconds = Column(Float, default=0.0)

    scanned_at = Column(DateTime, default=datetime.utcnow)

    target_db = relationship("TargetDatabase")