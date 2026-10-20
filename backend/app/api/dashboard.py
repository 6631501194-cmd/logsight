from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Alert, Log, User
from app.db.session import get_db
from app.security import current_user
from app.services.alerts import is_failed_login

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def groups(db: Session, column, tenant_id, limit: int = 10):
    rows = db.execute(select(column.label("value"), func.count(Log.id).label("count")).where(Log.tenant_id == tenant_id).group_by(column).order_by(func.count(Log.id).desc()).limit(limit)).all()
    return [{"value": row.value or "unknown", "count": row.count} for row in rows]


@router.get("/statistics")
def statistics(user: User = Depends(current_user), db: Session = Depends(get_db)) -> dict:
    base = Log.tenant_id == user.tenant_id
    failed = db.scalar(select(func.count(Log.id)).where(base, func.lower(Log.event_type).like("%login%"), func.lower(Log.event_type).like("%fail%"))) or 0
    alerts = db.scalar(select(func.count(Alert.id)).where(Alert.tenant_id == user.tenant_id)) or 0
    activity = db.execute(select(func.date_trunc("hour", Log.timestamp).label("bucket"), func.count(Log.id).label("count")).where(base).group_by("bucket").order_by("bucket")).all()
    return {"total_logs": db.scalar(select(func.count(Log.id)).where(base)) or 0, "failed_login_events": failed, "total_security_alerts": alerts, "by_severity": groups(db, Log.severity, user.tenant_id), "by_source": groups(db, Log.source, user.tenant_id), "top_source_ips": groups(db, Log.src_ip, user.tenant_id), "top_usernames": groups(db, Log.user_name, user.tenant_id), "top_event_types": groups(db, Log.event_type, user.tenant_id), "activity": [{"timestamp": row.bucket.isoformat(), "count": row.count} for row in activity]}
