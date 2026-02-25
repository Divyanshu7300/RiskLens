from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.scan_history import ScanHistory
from app.schemas.scan_schema import ScanHistoryResponse

router = APIRouter(prefix="/history", tags=["History"])


@router.get("", response_model=List[ScanHistoryResponse])
def list_scans(db: Session = Depends(get_db)):

    scans = (
        db.query(ScanHistory)
        .order_by(ScanHistory.scanned_at.desc())
        .limit(50)
        .all()
    )

    return scans