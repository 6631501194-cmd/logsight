from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import String, and_, cast, func, or_, select
from sqlalchemy.orm import Session

from app.db.models import Log, User
from app.db.session import get_db
from app.schemas import LogResponse, PageResponse
from app.security import current_user

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("", response_model=PageResponse)
def search_logs(
    keyword: str | None = None, severity: int | None = Query(default=None, ge=0, le=10), source: str | None = None,
    event_type: str | None = None, src_ip: str | None = None, start: datetime | None = None, end: datetime | None = None,
    page: int = Query(default=1, ge=1), page_size: int = Query(default=50, ge=1, le=100), sort: str = Query(default="desc", pattern="^(asc|desc)$"),
    tenant: str | None = None, user: User = Depends(current_user), db: Session = Depends(get_db),
) -> PageResponse:
    if tenant is not None and tenant != str(user.tenant_id):
        raise HTTPException(status_code=403, detail="Cross-tenant access is forbidden")
    filters = [Log.tenant_id == user.tenant_id]
    if keyword:
        term = f"%{keyword}%"
        filters.append(or_(Log.event_type.ilike(term), Log.user_name.ilike(term), Log.src_ip.ilike(term), cast(Log.raw, String).ilike(term)))
    for column, value in ((Log.severity, severity), (Log.source, source), (Log.event_type, event_type), (Log.src_ip, src_ip)):
        if value is not None:
            filters.append(column == value)
    if start: filters.append(Log.timestamp >= start)
    if end: filters.append(Log.timestamp <= end)
    total = db.scalar(select(func.count(Log.id)).where(and_(*filters))) or 0
    ordering = Log.timestamp.asc() if sort == "asc" else Log.timestamp.desc()
    logs = db.scalars(select(Log).where(and_(*filters)).order_by(ordering).offset((page - 1) * page_size).limit(page_size)).all()
    return PageResponse(items=[LogResponse(id=str(log.id), timestamp=log.timestamp, source=log.source, event_type=log.event_type, severity=log.severity, src_ip=log.src_ip, user_name=log.user_name, raw=log.raw) for log in logs], total=total, page=page, page_size=page_size)
