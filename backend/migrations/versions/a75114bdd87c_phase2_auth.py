"""phase2_auth — add last_login_at to users, create revoked_tokens

Revision ID: a75114bdd87c
Revises: a66166e960cd
Create Date: 2026-11-27 00:01:00.000000

Changes:
- users: add last_login_at TIMESTAMPTZ NULL
- new table: revoked_tokens (JTI-based token revocation)
"""
import sqlalchemy as sa
from alembic import op

revision = "a75114bdd87c"
down_revision = "a66166e960cd"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "revoked_tokens",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column("jti", sa.String(36), nullable=False),
        sa.Column("user_id", sa.String(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("jti", name="uq_revoked_tokens_jti"),
    )
    op.create_index("ix_revoked_tokens_jti", "revoked_tokens", ["jti"], unique=True)
    op.create_index("ix_revoked_tokens_expires_at", "revoked_tokens", ["expires_at"])


def downgrade() -> None:
    op.drop_index("ix_revoked_tokens_expires_at", table_name="revoked_tokens")
    op.drop_index("ix_revoked_tokens_jti", table_name="revoked_tokens")
    op.drop_table("revoked_tokens")
    op.drop_column("users", "last_login_at")
