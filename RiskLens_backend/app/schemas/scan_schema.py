from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ScanHistoryResponse(BaseModel):
    id: int
    scan_mode: str
    input_format: Optional[str]
    file_name: Optional[str]
    total_rules: Optional[int]
    total_violations: Optional[int]
    status: str
    duration_seconds: float
    scanned_at: datetime

    class Config:
        from_attributes = True