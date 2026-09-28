"""Initial tables: providers, dishes, demand_clusters

Revision ID: 0001
Revises: None
Create Date: 2026-09-28
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "providers",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("town", sa.String(100), nullable=False),
        sa.Column("area", sa.String(200), nullable=False),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lon", sa.Float, nullable=False),
        sa.Column("cuisines", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("diet_types", sa.JSON, nullable=False, server_default="[]"),
        sa.Column("capacity_total", sa.Integer, nullable=False),
        sa.Column("capacity_available", sa.Integer, nullable=False),
        sa.Column("list_price_monthly", sa.Float, nullable=False),
        sa.Column("cost_per_meal", sa.Float, nullable=False),
        sa.Column("min_margin", sa.Float, nullable=False),
        sa.Column("flexibility", sa.Float, nullable=False),
        sa.Column("rating", sa.Float, nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="approved"),
        sa.Column("consent_given", sa.Boolean, nullable=False, server_default="0"),
        sa.CheckConstraint("min_margin >= 0 AND min_margin <= 1", name="ck_min_margin"),
        sa.CheckConstraint("flexibility > 0 AND flexibility <= 1", name="ck_flexibility"),
        sa.CheckConstraint("rating >= 0 AND rating <= 5", name="ck_rating"),
        sa.CheckConstraint("status IN ('pending', 'approved')", name="ck_status"),
    )

    op.create_table(
        "dishes",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column(
            "provider_id",
            sa.String(64),
            sa.ForeignKey("providers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("slot", sa.String(10), nullable=False),
        sa.Column("diet", sa.String(10), nullable=False),
        sa.Column("cuisine", sa.String(50), nullable=False),
        sa.Column("main_item", sa.String(50), nullable=False),
        sa.Column("cost_tier", sa.Integer, nullable=False),
        sa.CheckConstraint("slot IN ('lunch', 'dinner')", name="ck_slot"),
        sa.CheckConstraint("diet IN ('veg', 'non_veg', 'egg')", name="ck_diet"),
        sa.CheckConstraint("cost_tier IN (1, 2, 3)", name="ck_cost_tier"),
    )

    op.create_table(
        "demand_clusters",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("town", sa.String(100), nullable=False),
        sa.Column("area", sa.String(200), nullable=False),
        sa.Column("lat", sa.Float, nullable=False),
        sa.Column("lon", sa.Float, nullable=False),
        sa.Column("headcount", sa.Integer, nullable=False),
        sa.Column("budget_ceiling_monthly", sa.Float, nullable=False),
        sa.Column("cuisine_weights", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("diet_split", sa.JSON, nullable=False, server_default="{}"),
        sa.Column("flexibility", sa.Float, nullable=False),
        sa.CheckConstraint("flexibility > 0 AND flexibility <= 1", name="ck_cluster_flex"),
    )


def downgrade() -> None:
    op.drop_table("demand_clusters")
    op.drop_table("dishes")
    op.drop_table("providers")
