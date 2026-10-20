from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from app.db.models import Alert, Log


def delete_expired_logs(db: Session, retention_days: int) -> int:
    if retention_days < 1:
        raise ValueError("retention_days must be at least one")
    cutoff = datetime.now(UTC) - timedelta(days=retention_days)
    expired_ids = select(Log.id).where(Log.timestamp < cutoff)
    db.execute(update(Alert).where(Alert.log_id.in_(expired_ids)).values(log_id=None))
    result = db.execute(delete(Log).where(Log.timestamp < cutoff))
    db.commit()
    return result.rowcount or 0
