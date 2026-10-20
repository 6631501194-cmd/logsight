from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Alert, User
from app.db.session import get_db
from app.security import current_user

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def list_alerts(severity: int | None = Query(default=None, ge=0, le=10), user: User = Depends(current_user), db: Session = Depends(get_db)) -> list[dict]:
    statement = select(Alert).where(Alert.tenant_id == user.tenant_id).order_by(Alert.created_at.desc())
    if severity is not None:
        statement = statement.where(Alert.severity == severity)
    return [{"id": str(item.id), "title": item.title, "severity": item.severity, "status": item.status, "details": item.details, "created_at": item.created_at} for item in db.scalars(statement).all()]
