from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, PageBreak
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import enums


def generate_audit_report(file_path, risk_data, violations):

    doc = SimpleDocTemplate(file_path)
    elements = []

    styles = getSampleStyleSheet()

    title_style = styles["Title"]
    heading_style = styles["Heading2"]
    normal_style = styles["Normal"]

    # ===============================
    # 🔥 TITLE PAGE
    # ===============================

    elements.append(Paragraph("PolicyGuard Compliance Audit Report", title_style))
    elements.append(Spacer(1, 0.5 * inch))

    generated_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    elements.append(Paragraph(f"Generated on: {generated_time}", normal_style))
    elements.append(Spacer(1, 0.5 * inch))

    # Big compliance score
    score_style = ParagraphStyle(
        name="ScoreStyle",
        parent=styles["Heading1"],
        alignment=enums.TA_CENTER,
        textColor=colors.darkblue
    )

    elements.append(
        Paragraph(f"Compliance Score: {risk_data['risk_score']}%", score_style)
    )
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(
        Paragraph(f"Risk Level: {risk_data['risk_level']}", styles["Heading3"])
    )

    elements.append(PageBreak())

    # ===============================
    # 🔥 RISK SUMMARY SECTION
    # ===============================

    elements.append(Paragraph("Risk Summary", heading_style))
    elements.append(Spacer(1, 0.3 * inch))

    summary_data = [
        ["Metric", "Value"],
        ["Total Violations", str(risk_data["total_violations"])],
        ["Risk Score", f"{risk_data['risk_score']}%"],
        ["Risk Level", risk_data["risk_level"]],
    ]

    summary_table = Table(summary_data, colWidths=[250, 200])
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(summary_table)
    elements.append(Spacer(1, 0.5 * inch))

    # ===============================
    # 🔥 SEVERITY DISTRIBUTION
    # ===============================

    critical_count = sum(1 for v in violations if v.severity.upper() == "CRITICAL")
    high_count = sum(1 for v in violations if v.severity.upper() == "HIGH")
    medium_count = sum(1 for v in violations if v.severity.upper() == "MEDIUM")

    severity_data = [
        ["Severity Level", "Count"],
        ["Critical", str(critical_count)],
        ["High", str(high_count)],
        ["Medium", str(medium_count)],
    ]

    severity_table = Table(severity_data, colWidths=[250, 200])
    severity_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
    ]))

    elements.append(severity_table)
    elements.append(PageBreak())

    # ===============================
    # 🔥 VIOLATION DETAILS
    # ===============================

    elements.append(Paragraph("Violation Details", heading_style))
    elements.append(Spacer(1, 0.3 * inch))

    # Sort by severity priority
    severity_order = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3}
    violations.sort(key=lambda v: severity_order.get(v.severity.upper(), 4))

    for i, v in enumerate(violations):

        # Severity color
        if v.severity.upper() == "CRITICAL":
            severity_color = colors.red
        elif v.severity.upper() == "HIGH":
            severity_color = colors.orange
        else:
            severity_color = colors.black

        severity_style = ParagraphStyle(
            name=f"SeverityStyle_{i}",
            parent=normal_style,
            textColor=severity_color
        )

        violation_data = [
            ["Rule", getattr(v.rule, "description", "N/A")],
            ["Table", v.table_name],
            ["Record ID", str(v.record_id)],
            ["Severity", v.severity],
            ["Message", getattr(v, "explanation", v.message)],
        ]

        violation_table = Table(violation_data, colWidths=[150, 300])
        violation_table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
        ]))

        elements.append(violation_table)
        elements.append(Spacer(1, 0.4 * inch))

        # Page break every 10 violations for readability
        if (i + 1) % 10 == 0:
            elements.append(PageBreak())

    doc.build(elements)