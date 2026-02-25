from pydantic import BaseModel
from typing import Optional

class SystemConfigResponse(BaseModel):
    id: int
    auto_scan_enabled: bool
    scan_interval_minutes: int

    class Config:
        from_attributes = True


class SystemConfigUpdate(BaseModel):
    auto_scan_enabled: Optional[bool] = None
    scan_interval_minutes: Optional[int] = None