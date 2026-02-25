from pydantic import BaseModel
from typing import Optional, Dict, Any

class RuleResponse(BaseModel):
    id: int
    policy_id: int
    table_name: str
    condition_json: Dict[str, Any]
    description: Optional[str]
    severity: str

    class Config:
        from_attributes = True