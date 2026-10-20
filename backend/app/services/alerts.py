import hashlib
from datetime import timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Alert, AlertRule, Log


def is_failed_login(event_type: str) -> bool:
    value = event_type.lower()
    return "login" in value and ("fail" in value or "denied" in value)


def evaluate_failed_login_rules(db: Session, log: Log) -> None:
    if not log.src_ip or not is_failed_login(log.event_type):
        return
    rules = db.scalars(select(AlertRule).where(AlertRule.tenant_id == log.tenant_id, AlertRule.rule_type == "failed_login_by_ip", AlertRule.is_active.is_(True))).all()
    for rule in rules:
        start = log.timestamp - timedelta(minutes=rule.window_minutes)
        count = db.scalar(select(func.count(Log.id)).where(Log.tenant_id == log.tenant_id, Log.src_ip == log.src_ip, Log.timestamp >= start, Log.timestamp <= log.timestamp, func.lower(Log.event_type).like("%login%"), func.lower(Log.event_type).like("%fail%"))) or 0
        if count < rule.threshold:
            continue
        bucket = int(log.timestamp.timestamp()) // (rule.window_minutes * 60)
        dedupe_key = hashlib.sha256(f"{rule.id}:{log.src_ip}:{bucket}".encode()).hexdigest()
        if db.scalar(select(Alert.id).where(Alert.dedupe_key == dedupe_key)) is None:
            db.add(Alert(tenant_id=log.tenant_id, rule_id=rule.id, log_id=log.id, title=f"Repeated failed logins from {log.src_ip}", severity=max(log.severity or 0, 7), details={"src_ip": log.src_ip, "count": count, "window_minutes": rule.window_minutes}, dedupe_key=dedupe_key))
