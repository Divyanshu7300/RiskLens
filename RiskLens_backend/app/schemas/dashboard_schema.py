from pydantic import BaseModel
from typing import Optional


class TopTable(BaseModel):
    table_name: str
    total_risk: int


class DashboardResponse(BaseModel):
    total_rules: int
    total_violations: int
    total_risk_score: int
    average_risk: float
    system_status: str
    top_risky_table: Optional[TopTable]