from sqlalchemy import Column, Integer, String
from app.core.database import Base

class TargetDatabase(Base):
    __tablename__ = "target_databases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    db_type = Column(String, nullable=False)  # postgres, mysql
    host = Column(String, nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)
    db_name = Column(String, nullable=False)