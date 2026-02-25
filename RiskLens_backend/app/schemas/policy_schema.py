from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PolicyResponse(BaseModel):
    id: int
    file_name: str
    extracted_text: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True