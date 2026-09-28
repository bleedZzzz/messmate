"""Repository layer: query DB, return Pydantic domain models.

Agents and API routes consume these functions — never ORM objects directly.
"""

from sqlalchemy.orm import Session

from app.db.tables import DemandClusterRow, DishRow, ProviderRow
from app.models.domain import DemandCluster, Dish, Provider

# ---------------------------------------------------------------------------
# Helpers: ORM → Pydantic
# ---------------------------------------------------------------------------


def _dish_from_row(row: DishRow) -> Dish:
    return Dish(
        id=row.id,
        name=row.name,
        slot=row.slot,  # type: ignore[arg-type]
        diet=row.diet,  # type: ignore[arg-type]
        cuisine=row.cuisine,
        main_item=row.main_item,
        cost_tier=row.cost_tier,  # type: ignore[arg-type]
    )


def _provider_from_row(row: ProviderRow) -> Provider:
    return Provider(
        id=row.id,
        name=row.name,
        town=row.town,
        area=row.area,
        lat=row.lat,
        lon=row.lon,
        cuisines=row.cuisines,
        diet_types=row.diet_types,
        capacity_total=row.capacity_total,
        capacity_available=row.capacity_available,
        list_price_monthly=row.list_price_monthly,
        cost_per_meal=row.cost_per_meal,
        min_margin=row.min_margin,
        flexibility=row.flexibility,
        rating=row.rating,
        dishes=[_dish_from_row(d) for d in row.dishes],
        phone=row.phone,
        status=row.status,  # type: ignore[arg-type]
    )


def _cluster_from_row(row: DemandClusterRow) -> DemandCluster:
    return DemandCluster(
        id=row.id,
        town=row.town,
        area=row.area,
        lat=row.lat,
        lon=row.lon,
        headcount=row.headcount,
        budget_ceiling_monthly=row.budget_ceiling_monthly,
        cuisine_weights=row.cuisine_weights,
        diet_split=row.diet_split,
        flexibility=row.flexibility,
    )


# ---------------------------------------------------------------------------
# Provider queries
# ---------------------------------------------------------------------------


def get_all_providers(session: Session) -> list[Provider]:
    """Return all providers with their dishes."""
    rows = session.query(ProviderRow).all()
    return [_provider_from_row(r) for r in rows]


def get_provider_by_id(session: Session, provider_id: str) -> Provider | None:
    """Return a single provider by ID, or None."""
    row = session.get(ProviderRow, provider_id)
    return _provider_from_row(row) if row else None


def get_providers_by_town(session: Session, town: str) -> list[Provider]:
    """Return all providers in a given town."""
    rows = session.query(ProviderRow).filter(ProviderRow.town == town).all()
    return [_provider_from_row(r) for r in rows]


def get_approved_providers(session: Session) -> list[Provider]:
    """Return only approved providers."""
    rows = session.query(ProviderRow).filter(ProviderRow.status == "approved").all()
    return [_provider_from_row(r) for r in rows]


# ---------------------------------------------------------------------------
# Demand cluster queries
# ---------------------------------------------------------------------------


def get_all_clusters(session: Session) -> list[DemandCluster]:
    """Return all demand clusters."""
    rows = session.query(DemandClusterRow).all()
    return [_cluster_from_row(r) for r in rows]


def get_clusters_by_town(session: Session, town: str) -> list[DemandCluster]:
    """Return clusters for a given town."""
    rows = session.query(DemandClusterRow).filter(DemandClusterRow.town == town).all()
    return [_cluster_from_row(r) for r in rows]


def get_cluster_by_id(session: Session, cluster_id: str) -> DemandCluster | None:
    """Return a single cluster by ID, or None."""
    row = session.get(DemandClusterRow, cluster_id)
    return _cluster_from_row(row) if row else None


# ---------------------------------------------------------------------------
# Bulk insert (used by seed.py)
# ---------------------------------------------------------------------------


def insert_provider(session: Session, provider: Provider, consent: bool = True) -> None:
    """Insert a provider and its dishes into the database."""
    row = ProviderRow(
        id=provider.id,
        name=provider.name,
        town=provider.town,
        area=provider.area,
        lat=provider.lat,
        lon=provider.lon,
        cuisines=provider.cuisines,
        diet_types=provider.diet_types,
        capacity_total=provider.capacity_total,
        capacity_available=provider.capacity_available,
        list_price_monthly=provider.list_price_monthly,
        cost_per_meal=provider.cost_per_meal,
        min_margin=provider.min_margin,
        flexibility=provider.flexibility,
        rating=provider.rating,
        phone=provider.phone,
        status=provider.status,
        consent_given=consent,
    )
    for dish in provider.dishes:
        row.dishes.append(
            DishRow(
                id=dish.id,
                name=dish.name,
                slot=dish.slot,
                diet=dish.diet,
                cuisine=dish.cuisine,
                main_item=dish.main_item,
                cost_tier=dish.cost_tier,
            )
        )
    session.add(row)


def insert_cluster(session: Session, cluster: DemandCluster) -> None:
    """Insert a demand cluster into the database."""
    row = DemandClusterRow(
        id=cluster.id,
        town=cluster.town,
        area=cluster.area,
        lat=cluster.lat,
        lon=cluster.lon,
        headcount=cluster.headcount,
        budget_ceiling_monthly=cluster.budget_ceiling_monthly,
        cuisine_weights=cluster.cuisine_weights,
        diet_split=cluster.diet_split,
        flexibility=cluster.flexibility,
    )
    session.add(row)


def count_providers(session: Session) -> int:
    """Return the total number of providers in the database."""
    return session.query(ProviderRow).count()


def count_clusters(session: Session) -> int:
    """Return the total number of demand clusters in the database."""
    return session.query(DemandClusterRow).count()
