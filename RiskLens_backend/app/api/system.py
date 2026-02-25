from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.system_config import SystemConfig
from app.schemas.system import SystemConfigResponse, SystemConfigUpdate

router = APIRouter(prefix="/system", tags=["System"])


# ─────────────────────────────────────────────
# Helper: Get or Create Singleton Config
# ─────────────────────────────────────────────
def get_or_create_config(db: Session) -> SystemConfig:
    config = db.query(SystemConfig).first()

    if not config:
        config = SystemConfig(
            auto_scan_enabled=False,
            scan_interval_minutes=60
        )
        db.add(config)
        db.commit()
        db.refresh(config)

    return config


# ─────────────────────────────────────────────
# GET SYSTEM CONFIG
# ─────────────────────────────────────────────
@router.get("", response_model=SystemConfigResponse)
def get_system_config(db: Session = Depends(get_db)):
    return get_or_create_config(db)


# ─────────────────────────────────────────────
# UPDATE SYSTEM CONFIG (Partial Update)
# ─────────────────────────────────────────────
@router.patch("", response_model=SystemConfigResponse)
def update_system_config(
    update_data: SystemConfigUpdate,
    db: Session = Depends(get_db)
):

    config = get_or_create_config(db)

    if update_data.auto_scan_enabled is not None:
        config.auto_scan_enabled = update_data.auto_scan_enabled

    if update_data.scan_interval_minutes is not None:

        if not (1 <= update_data.scan_interval_minutes <= 1440):
            raise HTTPException(
                status_code=400,
                detail="Interval must be between 1 and 1440 minutes"
            )

        config.scan_interval_minutes = update_data.scan_interval_minutes

    db.commit()
    db.refresh(config)

    return config