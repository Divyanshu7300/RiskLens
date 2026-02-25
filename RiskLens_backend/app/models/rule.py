from sqlalchemy import Column, Integer, String, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    
    policy_id = Column(Integer, ForeignKey("policies.id", ondelete="CASCADE"))

    # 🔥 IMPORTANT
    table_name = Column(String, nullable=False)
    
    # Flexible rule storage
    condition_json = Column(JSON, nullable=False)

    description = Column(String)
    severity = Column(String, default="Medium")

    policy = relationship("Policy", back_populates="rules")
    violations = relationship("Violation", back_populates="rule", cascade="all, delete")