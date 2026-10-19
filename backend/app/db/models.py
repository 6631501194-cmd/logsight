import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Tenant(Base):
    __tablename__ = "tenants"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(160))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="viewer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    tenant: Mapped[Tenant] = relationship()


class IngestionKey(Base):
    __tablename__ = "ingestion_keys"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), default="default")
    key_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    tenant: Mapped[Tenant] = relationship()


class Log(Base):
    __tablename__ = "logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    vendor: Mapped[str | None] = mapped_column(String(100))
    product: Mapped[str | None] = mapped_column(String(100))
    event_type: Mapped[str] = mapped_column(String(160), nullable=False, index=True)
    event_subtype: Mapped[str | None] = mapped_column(String(160))
    severity: Mapped[int | None] = mapped_column(Integer)
    action: Mapped[str | None] = mapped_column(String(50))
    src_ip: Mapped[str | None] = mapped_column(String(45), index=True)
    dst_ip: Mapped[str | None] = mapped_column(String(45))
    src_port: Mapped[int | None] = mapped_column(Integer)
    dst_port: Mapped[int | None] = mapped_column(Integer)
    protocol: Mapped[str | None] = mapped_column(String(20))
    user_name: Mapped[str | None] = mapped_column(String(255), index=True)
    host: Mapped[str | None] = mapped_column(String(255))
    process: Mapped[str | None] = mapped_column(String(255))
    url: Mapped[str | None] = mapped_column(Text)
    http_method: Mapped[str | None] = mapped_column(String(12))
    status_code: Mapped[int | None] = mapped_column(Integer)
    rule_name: Mapped[str | None] = mapped_column(String(255))
    rule_id: Mapped[str | None] = mapped_column(String(255))
    cloud: Mapped[dict] = mapped_column(JSONB, default=dict)
    raw: Mapped[dict] = mapped_column(JSONB, nullable=False)
    tags: Mapped[list] = mapped_column(JSONB, default=list)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__ = (
        Index("ix_logs_tenant_timestamp", "tenant_id", "timestamp"),
        Index("ix_logs_raw_gin", "raw", postgresql_using="gin"),
    )


class AlertRule(Base):
    __tablename__ = "alert_rules"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    rule_type: Mapped[str] = mapped_column(String(80), nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, default=5)
    window_minutes: Mapped[int] = mapped_column(Integer, default=5)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_alert_rule_tenant_name"),)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tenants.id"), nullable=False, index=True)
    rule_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("alert_rules.id"))
    log_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("logs.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[int] = mapped_column(Integer, default=5)
    status: Mapped[str] = mapped_column(String(30), default="open")
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
