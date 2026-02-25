from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.core.database import get_db
from app.models.violation import Violation

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.get("")
def get_risk_analysis(db: Session = Depends(get_db)):

    # ─────────────────────────────────────
    # BASIC AGGREGATES
    # ─────────────────────────────────────
    total_violations = db.query(func.count(Violation.id)).scalar() or 0
    total_risk = db.query(func.sum(Violation.risk_value)).scalar() or 0
    max_risk = db.query(func.max(Violation.risk_value)).scalar() or 0
    min_risk = db.query(func.min(Violation.risk_value)).scalar() or 0

    avg_risk = (
        total_risk / total_violations
        if total_violations > 0
        else 0
    )

    # ─────────────────────────────────────
    # RISK DISTRIBUTION (Value Frequency)
    # ─────────────────────────────────────
    distribution_query = (
        db.query(Violation.risk_value, func.count(Violation.id))
        .group_by(Violation.risk_value)
        .all()
    )

    risk_distribution = {
        str(risk): count for risk, count in distribution_query
    }

    # ─────────────────────────────────────
    # HIGH RISK % (threshold configurable)
    # ─────────────────────────────────────
    HIGH_RISK_THRESHOLD = 7

    high_risk_count = (
        db.query(func.count(Violation.id))
        .filter(Violation.risk_value >= HIGH_RISK_THRESHOLD)
        .scalar()
        or 0
    )

    high_risk_percentage = (
        (high_risk_count / total_violations) * 100
        if total_violations > 0
        else 0
    )

    # ─────────────────────────────────────
    # TOP 5 RISKY RULES
    # ─────────────────────────────────────
    top_rules_query = (
        db.query(
            Violation.rule_id,
            func.sum(Violation.risk_value).label("total_rule_risk")
        )
        .group_by(Violation.rule_id)
        .order_by(desc("total_rule_risk"))
        .limit(5)
        .all()
    )

    top_risky_rules = [
        {
            "rule_id": rule_id,
            "total_risk": total_rule_risk
        }
        for rule_id, total_rule_risk in top_rules_query
    ]

    # ─────────────────────────────────────
    # SYSTEM STATUS LOGIC
    # ─────────────────────────────────────
    if total_risk >= 200:
        status = "CRITICAL"
    elif total_risk >= 100:
        status = "HIGH"
    elif total_risk >= 40:
        status = "MEDIUM"
    else:
        status = "LOW"

    # ─────────────────────────────────────
    # FINAL RESPONSE
    # ─────────────────────────────────────
    return {
        "overview": {
            "total_violations": total_violations,
            "total_risk_score": total_risk,
            "average_risk": round(avg_risk, 2),
            "max_risk": max_risk,
            "min_risk": min_risk
        },
        "distribution": risk_distribution,
        "high_risk_percentage": round(high_risk_percentage, 2),
        "top_risky_rules": top_risky_rules,
        "system_status": status
    }