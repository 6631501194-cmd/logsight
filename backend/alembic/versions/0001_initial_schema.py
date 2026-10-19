"""initial LogSight schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-10-19
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("tenants", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("slug", sa.String(80), nullable=False), sa.Column("name", sa.String(160), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_tenants_slug", "tenants", ["slug"], unique=True)
    op.create_table("users", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("email", sa.String(255), nullable=False), sa.Column("password_hash", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"]); op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_table("ingestion_keys", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("name", sa.String(100), nullable=False), sa.Column("key_hash", sa.String(64), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")), sa.UniqueConstraint("key_hash"))
    op.create_index("ix_ingestion_keys_tenant_id", "ingestion_keys", ["tenant_id"])
    op.create_table("logs", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("source", sa.String(50), nullable=False), sa.Column("vendor", sa.String(100)), sa.Column("product", sa.String(100)), sa.Column("event_type", sa.String(160), nullable=False), sa.Column("event_subtype", sa.String(160)), sa.Column("severity", sa.Integer()), sa.Column("action", sa.String(50)), sa.Column("src_ip", sa.String(45)), sa.Column("dst_ip", sa.String(45)), sa.Column("src_port", sa.Integer()), sa.Column("dst_port", sa.Integer()), sa.Column("protocol", sa.String(20)), sa.Column("user_name", sa.String(255)), sa.Column("host", sa.String(255)), sa.Column("process", sa.String(255)), sa.Column("url", sa.Text()), sa.Column("http_method", sa.String(12)), sa.Column("status_code", sa.Integer()), sa.Column("rule_name", sa.String(255)), sa.Column("rule_id", sa.String(255)), sa.Column("cloud", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("raw", postgresql.JSONB(), nullable=False), sa.Column("tags", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")), sa.Column("ingested_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    for column in ["timestamp", "tenant_id", "source", "event_type", "src_ip", "user_name"]: op.create_index(f"ix_logs_{column}", "logs", [column])
    op.create_index("ix_logs_tenant_timestamp", "logs", ["tenant_id", "timestamp"]); op.create_index("ix_logs_raw_gin", "logs", ["raw"], postgresql_using="gin")
    op.create_table("alert_rules", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("name", sa.String(160), nullable=False), sa.Column("rule_type", sa.String(80), nullable=False), sa.Column("threshold", sa.Integer(), nullable=False), sa.Column("window_minutes", sa.Integer(), nullable=False), sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()), sa.UniqueConstraint("tenant_id", "name", name="uq_alert_rule_tenant_name"))
    op.create_index("ix_alert_rules_tenant_id", "alert_rules", ["tenant_id"])
    op.create_table("alerts", sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True), sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id"), nullable=False), sa.Column("rule_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("alert_rules.id")), sa.Column("log_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("logs.id")), sa.Column("title", sa.String(255), nullable=False), sa.Column("severity", sa.Integer(), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("details", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")))
    op.create_index("ix_alerts_tenant_id", "alerts", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("alerts"); op.drop_table("alert_rules"); op.drop_table("logs"); op.drop_table("ingestion_keys"); op.drop_table("users"); op.drop_table("tenants")
