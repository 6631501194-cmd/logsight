import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import AlertRule, IngestionKey, Tenant, User


def key_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def bootstrap_demo_data(db: Session) -> None:
    tenant = db.scalar(select(Tenant).where(Tenant.slug == settings.bootstrap_tenant_slug))
    if tenant is None:
        tenant = Tenant(slug=settings.bootstrap_tenant_slug, name=settings.bootstrap_tenant_name)
        db.add(tenant)
        db.flush()
    if db.scalar(select(IngestionKey).where(IngestionKey.key_hash == key_hash(settings.bootstrap_ingestion_key))) is None:
        db.add(IngestionKey(tenant_id=tenant.id, name="bootstrap", key_hash=key_hash(settings.bootstrap_ingestion_key)))
    if db.scalar(select(User).where(User.email == settings.bootstrap_admin_email)) is None:
        # Auth endpoints arrive in Phase 2; this seeds the required User entity without exposing a password.
        db.add(User(tenant_id=tenant.id, email=settings.bootstrap_admin_email, password_hash=key_hash(settings.bootstrap_admin_password), role="admin"))
    if db.scalar(select(AlertRule).where(AlertRule.tenant_id == tenant.id, AlertRule.name == "Repeated failed logins")) is None:
        db.add(AlertRule(tenant_id=tenant.id, name="Repeated failed logins", rule_type="failed_login_by_ip", threshold=5, window_minutes=5))
    db.commit()
