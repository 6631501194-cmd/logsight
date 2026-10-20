import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from pwdlib import PasswordHash

from app.db.models import AlertRule, IngestionKey, Tenant, User


def key_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ensure_ingestion_key(db: Session, tenant: Tenant, name: str, secret: str) -> None:
    """Idempotently register a tenant-bound key while storing only its hash."""
    if db.scalar(select(IngestionKey).where(IngestionKey.key_hash == key_hash(secret))) is None:
        db.add(IngestionKey(tenant_id=tenant.id, name=name, key_hash=key_hash(secret)))


def bootstrap_demo_data(db: Session) -> None:
    tenant = db.scalar(select(Tenant).where(Tenant.slug == settings.bootstrap_tenant_slug))
    if tenant is None:
        tenant = Tenant(slug=settings.bootstrap_tenant_slug, name=settings.bootstrap_tenant_name)
        db.add(tenant)
        db.flush()
    ensure_ingestion_key(db, tenant, "bootstrap", settings.bootstrap_ingestion_key)
    password_hash = PasswordHash.recommended()
    bootstrap_user = db.scalar(select(User).where(User.email == settings.bootstrap_admin_email))
    if bootstrap_user is None:
        db.add(User(tenant_id=tenant.id, email=settings.bootstrap_admin_email, password_hash=password_hash.hash(settings.bootstrap_admin_password), role="admin"))
    else:
        # Upgrade the Phase 1 development seed's legacy SHA-256 hash and keep its
        # password synchronized with the local-development environment value.
        bootstrap_user.password_hash = password_hash.hash(settings.bootstrap_admin_password)
    if db.scalar(select(AlertRule).where(AlertRule.tenant_id == tenant.id, AlertRule.name == "Repeated failed logins")) is None:
        db.add(AlertRule(tenant_id=tenant.id, name="Repeated failed logins", rule_type="failed_login_by_ip", threshold=5, window_minutes=5))
    db.commit()


    for slug, name, credentials in (
        ("demoA", "Demo A", ((settings.demo_a_admin_email, settings.demo_a_admin_password, "admin"), (settings.demo_a_viewer_email, settings.demo_a_viewer_password, "viewer"))),
        ("demoB", "Demo B", ((settings.demo_b_admin_email, settings.demo_b_admin_password, "admin"), (settings.demo_b_viewer_email, settings.demo_b_viewer_password, "viewer"))),
    ):
        demo_tenant = db.scalar(select(Tenant).where(Tenant.slug == slug))
        if demo_tenant is None:
            demo_tenant = Tenant(slug=slug, name=name)
            db.add(demo_tenant)
            db.flush()
        for email, password, role in credentials:
            if db.scalar(select(User).where(User.email == email)) is None:
                db.add(User(tenant_id=demo_tenant.id, email=email, password_hash=password_hash.hash(password), role=role))
        tenant_key = settings.demo_a_ingestion_key if slug == "demoA" else settings.demo_b_ingestion_key
        ensure_ingestion_key(db, demo_tenant, "sample-data-generator", tenant_key)
        if db.scalar(select(AlertRule).where(AlertRule.tenant_id == demo_tenant.id, AlertRule.rule_type == "failed_login_by_ip")) is None:
            db.add(AlertRule(tenant_id=demo_tenant.id, name="Repeated failed logins", rule_type="failed_login_by_ip", threshold=5, window_minutes=5))
    db.commit()
