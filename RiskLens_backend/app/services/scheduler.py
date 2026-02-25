import threading
import time
from sqlalchemy import text

from app.core.database import SessionLocal
from app.models.rule import Rule
from app.models.scan_history import ScanHistory
from app.models.system_config import SystemConfig
from app.models.violation import Violation


ALLOWED_OPERATORS = {"=", "==", "!=", "<", ">", "<=", ">="}


# ─────────────────────────────────────────────
# Inline Compliance Logic for Auto Scan
# ─────────────────────────────────────────────
def run_auto_scan(db, rules):

    violations = []

    for rule in rules:
        table = rule.table_name
        condition = rule.condition_json

        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if not table or not field or operator not in ALLOWED_OPERATORS:
            continue

        query = text(f"""
            SELECT * FROM {table}
            WHERE NOT ({field} {operator} :value)
        """)

        try:
            result = db.execute(query, {"value": value})
            rows = result.fetchall()
        except Exception:
            continue

        for row in rows:
            violations.append(
                Violation(
                    rule_id=rule.id,
                    table_name=table,
                    record_id=row[0],
                    message=f"{field} {operator} {value} violated",
                    severity=rule.severity,
                    remediation="Auto detected violation"
                )
            )

    return violations


# ─────────────────────────────────────────────
# Background Auto Scan Thread
# ─────────────────────────────────────────────
def auto_scan():

    while True:

        db = SessionLocal()

        try:
            config = db.query(SystemConfig).first()

            if not config:
                time.sleep(300)
                continue

            interval = config.scan_interval_minutes * 60

            if config.auto_scan_enabled:

                start_time = time.time()

                try:
                    rules = db.query(Rule).all()

                    violations = run_auto_scan(db, rules)

                    for v in violations:
                        db.add(v)

                    duration = time.time() - start_time

                    log = ScanHistory(
                        scan_mode="database",
                        total_rules=len(rules),
                        total_violations=len(violations),
                        status="AUTO_SUCCESS",
                        duration_seconds=duration
                    )

                    db.add(log)
                    db.commit()

                except Exception as e:
                    db.rollback()

                    duration = time.time() - start_time

                    log = ScanHistory(
                        scan_mode="database",
                        total_rules=0,
                        total_violations=0,
                        status="AUTO_FAILED",
                        duration_seconds=duration
                    )

                    db.add(log)
                    db.commit()

                    print("Auto Scan Error:", e)

        finally:
            db.close()

        time.sleep(interval if config else 300)


# ─────────────────────────────────────────────
# Start Thread
# ─────────────────────────────────────────────
def start_scheduler():
    thread = threading.Thread(target=auto_scan, daemon=True)
    thread.start()