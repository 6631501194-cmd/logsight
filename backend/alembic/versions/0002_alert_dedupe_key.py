"""add alert deduplication key

Revision ID: 0002_alert_dedupe
Revises: 0001_initial
Create Date: 2026-10-19
"""
from alembic import op
import sqlalchemy as sa

revision = "0002_alert_dedupe"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("alerts", sa.Column("dedupe_key", sa.String(128), nullable=True))
    op.create_unique_constraint("uq_alerts_dedupe_key", "alerts", ["dedupe_key"])


def downgrade() -> None:
    op.drop_constraint("uq_alerts_dedupe_key", "alerts", type_="unique")
    op.drop_column("alerts", "dedupe_key")
