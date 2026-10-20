import hashlib

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import IngestionKey, Log, Tenant
from app.db.session import get_db
from app.schemas import IngestRequest, IngestResponse
from app.services.normalization import normalize_log
from app.services.alerts import evaluate_failed_login_rules

router = APIRouter(tags=["ingestion"])


def authenticated_tenant(
    x_ingestion_key: str | None = Header(default=None), db: Session = Depends(get_db)
) -> Tenant:
    if not x_ingestion_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Ingestion-Key is required")
    digest = hashlib.sha256(x_ingestion_key.encode("utf-8")).hexdigest()
    key = db.scalar(
        select(IngestionKey).join(Tenant).where(IngestionKey.key_hash == digest, IngestionKey.is_active.is_(True), Tenant.is_active.is_(True))
    )
    if key is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid ingestion key")
    return key.tenant


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_log(payload: IngestRequest, tenant: Tenant = Depends(authenticated_tenant), db: Session = Depends(get_db)) -> IngestResponse:
    normalized = normalize_log(payload)
    # The authenticated key, not an untrusted request field, defines the owning tenant.
    log = Log(tenant_id=tenant.id, **normalized)
    db.add(log)
    db.flush()
    evaluate_failed_login_rules(db, log)
    db.commit()
    db.refresh(log)
    return IngestResponse(id=str(log.id), tenant=tenant.slug, source=log.source, timestamp=log.timestamp)
