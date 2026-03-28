"""create payments and outbox tables

Revision ID: 20260326_01
Revises: 
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "20260326_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "payments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("idempotency_key", sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column("amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("webhook_url", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "succeeded", "failed", name="payment_status", native_enum=False),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "outbox",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_outbox_created_at"), "outbox", ["created_at"], unique=False)
    op.create_index(op.f("ix_outbox_processed_at"), "outbox", ["processed_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_outbox_processed_at"), table_name="outbox")
    op.drop_index(op.f("ix_outbox_created_at"), table_name="outbox")
    op.drop_table("outbox")
    op.drop_table("payments")
