"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-06-14
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("keycloak_id", sa.String(36), unique=True),
        sa.Column(
            "role",
            sa.Enum("client", "advisor", "admin", name="userrole"),
            nullable=False,
            server_default="client",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "clients",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("code", sa.String(20), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "tier",
            sa.Enum("HNWI", "UHNWI", name="clienttier"),
            nullable=False,
            server_default="HNWI",
        ),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "portfolios",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("client_id", sa.String(36), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="USD"),
        sa.Column("inception_date", sa.Date, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "deals",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("portfolio_id", sa.String(36), sa.ForeignKey("portfolios.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "asset_class",
            sa.Enum("RE", "PE", "EQ", "CR", name="assetclass"),
            nullable=False,
        ),
        sa.Column(
            "geography",
            sa.Enum("Asia", "North America", "Europe", "Global", "Middle East", name="geography"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("active", "exited", name="dealstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("commitment", sa.Numeric(18, 2), nullable=False),
        sa.Column("nav", sa.Numeric(18, 2), nullable=False),
        sa.Column("cost_basis", sa.Numeric(18, 2), nullable=False),
        sa.Column("entry_date", sa.Date, nullable=False),
        sa.Column("exit_date", sa.Date),
        sa.Column("description", sa.Text),
    )

    op.create_table(
        "cashflows",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("deal_id", sa.String(36), sa.ForeignKey("deals.id"), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("amount", sa.Numeric(18, 2), nullable=False),
        sa.Column(
            "type",
            sa.Enum("contribution", "distribution", "nav", name="cashflowtype"),
            nullable=False,
        ),
        sa.UniqueConstraint("deal_id", "date", "type", name="uq_cashflow"),
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("client_id", sa.String(36), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False, server_default="web"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "messages",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "conversation_id",
            sa.String(36),
            sa.ForeignKey("conversations.id"),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.Enum("user", "assistant", "system", name="messagerole"),
            nullable=False,
        ),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("agent_id", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("messages")
    op.drop_table("conversations")
    op.drop_table("cashflows")
    op.drop_table("deals")
    op.drop_table("portfolios")
    op.drop_table("clients")
    op.drop_table("users")
    for enum in [
        "userrole",
        "clienttier",
        "assetclass",
        "geography",
        "dealstatus",
        "cashflowtype",
        "messagerole",
    ]:
        sa.Enum(name=enum).drop(op.get_bind(), checkfirst=True)
