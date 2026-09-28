"""SQLAlchemy ORM table definitions.

Tables: providers, dishes, demand_clusters.
JSON columns are portable across SQLite and PostgreSQL.
"""

from sqlalchemy import (
    JSON,
    CheckConstraint,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ProviderRow(Base):
    """ORM model for the providers table."""

    __tablename__ = "providers"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    town: Mapped[str] = mapped_column(String(100))
    area: Mapped[str] = mapped_column(String(200))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    cuisines: Mapped[list] = mapped_column(JSON, default=list)
    diet_types: Mapped[list] = mapped_column(JSON, default=list)
    capacity_total: Mapped[int] = mapped_column(Integer)
    capacity_available: Mapped[int] = mapped_column(Integer)
    list_price_monthly: Mapped[float] = mapped_column(Float)
    cost_per_meal: Mapped[float] = mapped_column(Float)
    min_margin: Mapped[float] = mapped_column(Float)
    flexibility: Mapped[float] = mapped_column(Float)
    rating: Mapped[float] = mapped_column(Float)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="approved")
    consent_given: Mapped[bool] = mapped_column(default=False)

    dishes: Mapped[list["DishRow"]] = relationship(
        back_populates="provider", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint("min_margin >= 0 AND min_margin <= 1", name="ck_min_margin"),
        CheckConstraint("flexibility > 0 AND flexibility <= 1", name="ck_flexibility"),
        CheckConstraint("rating >= 0 AND rating <= 5", name="ck_rating"),
        CheckConstraint("status IN ('pending', 'approved')", name="ck_status"),
    )


class DishRow(Base):
    """ORM model for the dishes table."""

    __tablename__ = "dishes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    provider_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("providers.id", ondelete="CASCADE")
    )
    name: Mapped[str] = mapped_column(String(200))
    slot: Mapped[str] = mapped_column(String(10))
    diet: Mapped[str] = mapped_column(String(10))
    cuisine: Mapped[str] = mapped_column(String(50))
    main_item: Mapped[str] = mapped_column(String(50))
    cost_tier: Mapped[int] = mapped_column(Integer)

    provider: Mapped["ProviderRow"] = relationship(back_populates="dishes")

    __table_args__ = (
        CheckConstraint("slot IN ('lunch', 'dinner')", name="ck_slot"),
        CheckConstraint("diet IN ('veg', 'non_veg', 'egg')", name="ck_diet"),
        CheckConstraint("cost_tier IN (1, 2, 3)", name="ck_cost_tier"),
    )


class DemandClusterRow(Base):
    """ORM model for the demand_clusters table."""

    __tablename__ = "demand_clusters"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    town: Mapped[str] = mapped_column(String(100))
    area: Mapped[str] = mapped_column(String(200))
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    headcount: Mapped[int] = mapped_column(Integer)
    budget_ceiling_monthly: Mapped[float] = mapped_column(Float)
    cuisine_weights: Mapped[dict] = mapped_column(JSON, default=dict)
    diet_split: Mapped[dict] = mapped_column(JSON, default=dict)
    flexibility: Mapped[float] = mapped_column(Float)

    __table_args__ = (
        CheckConstraint("flexibility > 0 AND flexibility <= 1", name="ck_cluster_flex"),
    )
