from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.models.violation import Violation
from app.models.rule import Rule

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("")
def get_dashboard(
    scan_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):

    base_query = db.query(Violation)

    if scan_id is not None:
        base_query = base_query.filter(Violation.scan_id == scan_id)

    # ───────────── Basic Metrics ─────────────
    total_violations = base_query.count()

    total_risk = base_query.with_entities(
        func.coalesce(func.sum(Violation.risk_value), 0)
    ).scalar()

    avg_risk = total_risk / total_violations if total_violations else 0

    # Count distinct rules involved in this scan
    total_rules = base_query.with_entities(
        func.count(func.distinct(Violation.rule_id))
    ).scalar() or 0

    # ───────────── Top Risky Table ─────────────
    top_table_query = (
        base_query
        .with_entities(
            Violation.table_name,
            func.sum(Violation.risk_value).label("table_risk")
        )
        .group_by(Violation.table_name)
        .order_by(desc("table_risk"))
        .first()
    )

    top_table = (
        {
            "table_name": top_table_query[0],
            "total_risk": top_table_query[1]
        }
        if top_table_query
        else None
    )

    # ───────────── System Health Logic ─────────────
    if avg_risk >= 8:
        status = "CRITICAL"
    elif avg_risk >= 5:
        status = "HIGH"
    elif avg_risk >= 3:
        status = "MEDIUM"
    else:
        status = "LOW"

    return {
        "total_rules_triggered": total_rules,
        "total_violations": total_violations,
        "total_risk_score": total_risk,
        "average_risk": round(avg_risk, 2),
        "system_status": status,
        "top_risky_table": top_table
    }