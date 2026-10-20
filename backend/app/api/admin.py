from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import User
from app.db.session import get_db
from app.security import require_admin
from app.services.retention import delete_expired_logs

router = APIRouter(prefix="/api/admin", tags=["administration"])


@router.post("/retention/run")
def run_retention(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> dict[str, int]:
    return {"deleted_logs": delete_expired_logs(db, settings.retention_days)}
