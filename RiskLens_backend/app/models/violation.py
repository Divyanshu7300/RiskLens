from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Violation(Base):
    __tablename__ = "violations"

    id = Column(Integer, primary_key=True, index=True)

    # Link to rule
    rule_id = Column(Integer, ForeignKey("rules.id", ondelete="CASCADE"))

    # Optional: Link to scan (VERY important for multi-dataset tracking)
    scan_id = Column(Integer, ForeignKey("scan_history.id", ondelete="CASCADE"))

    # Where violation occurred
    table_name = Column(String, nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)

    # Detailed info
    field_name = Column(String, nullable=False)
    actual_value = Column(String, nullable=True)
    expected_condition = Column(String, nullable=True)
    explanation = Column(String)

    # 🔥 Numeric risk model
    risk_value = Column(Integer, nullable=False, default=1, index=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    rule = relationship("Rule", back_populates="violations")
    scan = relationship("ScanHistory", back_populates="violations")


# Optional: Composite index for faster analytics
Index("idx_scan_risk", Violation.scan_id, Violation.risk_value)