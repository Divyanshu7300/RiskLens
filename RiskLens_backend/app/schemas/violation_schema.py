from pydantic import BaseModel
from datetime import datetime

class ViolationResponse(BaseModel):
    id: int
    table_name: str
    record_id: int
    field_name: str
    explanation: str
    severity: str
    created_at: datetime

    class Config:
        from_attributes = True