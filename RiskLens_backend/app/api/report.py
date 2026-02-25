from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import os
import uuid

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from app.core.database import get_db
from app.models.violation import Violation

router = APIRouter(prefix="/reports", tags=["Reports"])


# ─────────────────────────────────────────────
# PDF GENERATION FUNCTION (defined here)
# ─────────────────────────────────────────────
def generate_pdf_report(file_path: str, report_data: dict):
    doc = SimpleDocTemplate(file_path)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Compliance Analysis Report", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    elements.append(
        Paragraph(f"Generated At: {report_data['generated_at']}", styles["Normal"])
    )
    elements.append(Spacer(1, 0.3 * inch))

    overview = report_data["overview"]

    elements.append(Paragraph("Overview", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(f"Total Violations: {overview['total_violations']}", styles["Normal"]))
    elements.append(Paragraph(f"Total Risk Score: {overview['total_risk_score']}", styles["Normal"]))
    elements.append(Paragraph(f"Average Risk: {overview['average_risk']}", styles["Normal"]))
    elements.append(Paragraph(f"System Status: {overview['status']}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Top Risky Tables", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    for table in report_data["top_tables"]:
        elements.append(
            Paragraph(
                f"{table['table_name']} - Total Risk: {table['total_risk']}",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Top Risky Rules", styles["Heading2"]))
    elements.append(Spacer(1, 0.2 * inch))

    for rule in report_data["top_rules"]:
        elements.append(
            Paragraph(
                f"Rule {rule['rule_id']} - Total Risk: {rule['total_risk']}",
                styles["Normal"]
            )
        )

    doc.build(elements)


# ─────────────────────────────────────────────
# MAIN REPORT ENDPOINT
# ─────────────────────────────────────────────
@router.post("")
def create_report(
    scan_id: int | None = Query(default=None),
    db: Session = Depends(get_db)
):

    base_query = db.query(Violation)

    if scan_id:
        base_query = base_query.filter(Violation.scan_id == scan_id)

    total_violations = base_query.count()
    total_risk = base_query.with_entities(func.sum(Violation.risk_value)).scalar() or 0

    if total_violations == 0:
        raise HTTPException(404, "No violations found for report generation")

    avg_risk = total_risk / total_violations

    top_tables_query = (
        base_query
        .with_entities(
            Violation.table_name,
            func.sum(Violation.risk_value).label("table_risk")
        )
        .group_by(Violation.table_name)
        .order_by(desc("table_risk"))
        .limit(5)
        .all()
    )

    top_tables = [
        {"table_name": table, "total_risk": risk}
        for table, risk in top_tables_query
    ]

    top_rules_query = (
        base_query
        .with_entities(
            Violation.rule_id,
            func.sum(Violation.risk_value).label("rule_risk")
        )
        .group_by(Violation.rule_id)
        .order_by(desc("rule_risk"))
        .limit(5)
        .all()
    )

    top_rules = [
        {"rule_id": rule, "total_risk": risk}
        for rule, risk in top_rules_query
    ]

    if total_risk >= 200:
        status = "CRITICAL"
    elif total_risk >= 100:
        status = "HIGH"
    elif total_risk >= 40:
        status = "MEDIUM"
    else:
        status = "LOW"

    report_data = {
        "generated_at": datetime.utcnow(),
        "scan_id": scan_id,
        "overview": {
            "total_violations": total_violations,
            "total_risk_score": total_risk,
            "average_risk": round(avg_risk, 2),
            "status": status
        },
        "top_tables": top_tables,
        "top_rules": top_rules
    }

    os.makedirs("reports", exist_ok=True)

    file_name = f"report_{uuid.uuid4().hex}.pdf"
    file_path = os.path.join("reports", file_name)

    generate_pdf_report(file_path, report_data)

    return FileResponse(
        path=file_path,
        filename="Compliance_Analysis_Report.pdf",
        media_type="application/pdf"
    )