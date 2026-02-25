from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine, inspect, text
import pandas as pd
import tempfile
import os
from typing import Optional

from app.core.database import get_db, create_dynamic_engine
from app.models.policy import Policy
from app.models.rule import Rule
from app.models.violation import Violation
from app.models.scan_history import ScanHistory
from app.services.ai_rule_engine import extract_rules_with_ai
from app.services.pdf_service import extract_text_from_pdf

router = APIRouter(prefix="/scan", tags=["Scan"])


# ─────────────────────────────────────────────
# Severity → Numeric Risk Mapping
# ─────────────────────────────────────────────
def severity_to_risk(severity: str) -> int:
    mapping = {
        "Low": 1,
        "Medium": 3,
        "High": 5,
        "Critical": 8
    }
    return mapping.get(severity, 3)


# ─────────────────────────────────────────────
# MAIN SCAN ENDPOINT
# ─────────────────────────────────────────────
@router.post("")
async def scan(
    policy_file: UploadFile = File(...),
    db_uri: Optional[str] = None,
    data_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
):

    if not db_uri and not data_file:
        raise HTTPException(400, "Provide either db_uri or dataset file")

    policy_path = None
    dataset_path = None
    target_engine = None

    try:
        # ───────────── POLICY EXTRACTION ─────────────
        content = await policy_file.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(content)
            policy_path = tmp.name

        if policy_file.filename.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(policy_path)
        else:
            extracted_text = content.decode("utf-8", errors="ignore")

        if not extracted_text.strip():
            raise HTTPException(400, "Policy contains no readable text")

        # ───────────── DATA SOURCE ─────────────
        if db_uri:
            target_engine = create_dynamic_engine(db_uri)
            scan_mode = "database"
        else:
            dataset_content = await data_file.read()

            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(dataset_content)
                dataset_path = tmp.name

            filename_lower = data_file.filename.lower()

            if filename_lower.endswith(".csv"):
                df = pd.read_csv(dataset_path)
            elif filename_lower.endswith((".xlsx", ".xls")):
                df = pd.read_excel(dataset_path)
            elif filename_lower.endswith(".json"):
                df = pd.read_json(dataset_path)
            else:
                raise HTTPException(400, "Supported formats: CSV, XLSX, JSON")

            target_engine = create_engine("sqlite:///:memory:")
            df.to_sql("temp_table", target_engine, if_exists="replace", index=False)

            scan_mode = "file"

        inspector = inspect(target_engine)
        schema = {
            table: [col["name"] for col in inspector.get_columns(table)]
            for table in inspector.get_table_names()
        }

        if not schema:
            raise HTTPException(400, "No tables found in data source")

        # ───────────── MAIN TRANSACTION ─────────────
        with db.begin():

            # Save policy
            policy = Policy(
                file_name=policy_file.filename,
                extracted_text=extracted_text
            )
            db.add(policy)
            db.flush()

            # Create scan history
            scan_record = ScanHistory(
                scan_mode=scan_mode,
                total_rules=0,
                total_violations=0,
                status="PROCESSING"
            )
            db.add(scan_record)
            db.flush()

            # Extract AI rules
            ai_rules = extract_rules_with_ai(extracted_text, schema)

            if not ai_rules:
                raise HTTPException(422, "AI could not extract rules")

            rules = []

            for r in ai_rules:
                rule = Rule(
                    policy_id=policy.id,
                    table_name=r["table_name"],
                    condition_json={
                        "field": r["field"],
                        "operator": r["operator"],
                        "value": r["value"]
                    },
                    description=f"{r['field']} {r['operator']} {r['value']}",
                    severity=r.get("severity", "Medium")
                )
                db.add(rule)
                rules.append(rule)

            db.flush()

            # Run compliance scan
            TargetSession = sessionmaker(bind=target_engine)
            target_db = TargetSession()

            violations = []

            try:
                for rule in rules:

                    field = rule.condition_json.get("field")
                    operator = rule.condition_json.get("operator")
                    value = rule.condition_json.get("value")

                    query = text(f"""
                        SELECT * FROM {rule.table_name}
                        WHERE NOT ({field} {operator} :value)
                    """)

                    result = target_db.execute(query, {"value": value})
                    rows = result.fetchall()

                    for row in rows:
                        violations.append(
                            Violation(
                                rule_id=rule.id,
                                scan_id=scan_record.id,
                                table_name=rule.table_name,
                                record_id=row[0],
                                field_name=field,
                                actual_value=str(row[0]),
                                expected_condition=f"{operator} {value}",
                                explanation="Rule condition violated",
                                risk_value=severity_to_risk(rule.severity)
                            )
                        )

            finally:
                target_db.close()

            for v in violations:
                db.add(v)

            # Update scan summary
            scan_record.total_rules = len(rules)
            scan_record.total_violations = len(violations)
            scan_record.status = "SUCCESS" if violations else "NO_VIOLATIONS"

        return {
            "status": "success",
            "scan_id": scan_record.id,
            "total_rules": len(rules),
            "violations_found": len(violations),
            "scan_mode": scan_mode
        }

    except Exception as e:
        raise HTTPException(500, f"Scan failed: {str(e)}")

    finally:
        if target_engine:
            target_engine.dispose()

        for path in [policy_path, dataset_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except:
                    pass