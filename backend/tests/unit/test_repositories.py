"""Tests for the repository layer and database seeding."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.data.seed import seed_database
from app.data.synthetic_generator import generate_clusters, generate_providers
from app.db.base import Base
from app.db.repositories import (
    count_clusters,
    count_providers,
    get_all_clusters,
    get_all_providers,
    get_approved_providers,
    get_cluster_by_id,
    get_clusters_by_town,
    get_provider_by_id,
    get_providers_by_town,
    insert_cluster,
    insert_provider,
)


@pytest.fixture
def db_session() -> Session:  # type: ignore[misc]
    """Create an in-memory SQLite database and return a session."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    session = factory()
    yield session  # type: ignore[misc]
    session.close()


class TestProviderRepository:
    def test_insert_and_retrieve_provider(self, db_session: Session) -> None:
        providers = generate_providers(seed=42)
        p = providers[0]
        insert_provider(db_session, p)
        db_session.commit()

        retrieved = get_provider_by_id(db_session, p.id)
        assert retrieved is not None
        assert retrieved.id == p.id
        assert retrieved.name == p.name
        assert retrieved.town == p.town
        assert retrieved.cuisines == p.cuisines
        assert retrieved.diet_types == p.diet_types
        assert len(retrieved.dishes) == len(p.dishes)

    def test_dishes_round_trip(self, db_session: Session) -> None:
        providers = generate_providers(seed=42)
        p = providers[0]
        insert_provider(db_session, p)
        db_session.commit()

        retrieved = get_provider_by_id(db_session, p.id)
        assert retrieved is not None
        original_ids = sorted(d.id for d in p.dishes)
        retrieved_ids = sorted(d.id for d in retrieved.dishes)
        assert original_ids == retrieved_ids

    def test_get_nonexistent_provider(self, db_session: Session) -> None:
        assert get_provider_by_id(db_session, "nonexistent") is None

    def test_get_providers_by_town(self, db_session: Session) -> None:
        providers = generate_providers(seed=42)
        for p in providers[:5]:
            insert_provider(db_session, p)
        db_session.commit()

        town = providers[0].town
        town_providers = get_providers_by_town(db_session, town)
        assert all(p.town == town for p in town_providers)

    def test_get_approved_providers(self, db_session: Session) -> None:
        providers = generate_providers(seed=42)
        for p in providers[:3]:
            insert_provider(db_session, p)
        db_session.commit()

        approved = get_approved_providers(db_session)
        assert all(p.status == "approved" for p in approved)


class TestClusterRepository:
    def test_insert_and_retrieve_cluster(self, db_session: Session) -> None:
        clusters = generate_clusters(seed=42)
        c = clusters[0]
        insert_cluster(db_session, c)
        db_session.commit()

        retrieved = get_cluster_by_id(db_session, c.id)
        assert retrieved is not None
        assert retrieved.id == c.id
        assert retrieved.town == c.town
        assert retrieved.cuisine_weights == c.cuisine_weights
        assert retrieved.diet_split == c.diet_split

    def test_get_nonexistent_cluster(self, db_session: Session) -> None:
        assert get_cluster_by_id(db_session, "nonexistent") is None

    def test_get_clusters_by_town(self, db_session: Session) -> None:
        clusters = generate_clusters(seed=42)
        for c in clusters:
            insert_cluster(db_session, c)
        db_session.commit()

        town = clusters[0].town
        town_clusters = get_clusters_by_town(db_session, town)
        assert len(town_clusters) >= 2
        assert all(c.town == town for c in town_clusters)


class TestSeedIdempotency:
    def test_seed_populates_empty_db(self, db_session: Session) -> None:
        result = seed_database(db_session, seed=42)
        assert result["providers"] > 0
        assert result["clusters"] > 0
        assert count_providers(db_session) == result["providers"]
        assert count_clusters(db_session) == result["clusters"]

    def test_seed_is_idempotent(self, db_session: Session) -> None:
        first = seed_database(db_session, seed=42)
        second = seed_database(db_session, seed=42)

        # Second call should skip
        assert second["providers"] == 0
        assert second["clusters"] == 0

        # Counts unchanged
        assert count_providers(db_session) == first["providers"]
        assert count_clusters(db_session) == first["clusters"]

    def test_seeded_data_retrieval(self, db_session: Session) -> None:
        seed_database(db_session, seed=42)
        providers = get_all_providers(db_session)
        clusters = get_all_clusters(db_session)

        assert len(providers) > 0
        assert len(clusters) > 0
        # Every provider should have dishes
        for p in providers:
            assert len(p.dishes) >= 2, f"Provider {p.id} has {len(p.dishes)} dishes"


class TestCountsPerTown:
    """Print counts per town (verifies data distribution)."""

    def test_print_counts(self, db_session: Session) -> None:
        seed_database(db_session, seed=42)
        providers = get_all_providers(db_session)
        clusters = get_all_clusters(db_session)

        towns_p: dict[str, int] = {}
        towns_c: dict[str, int] = {}
        for p in providers:
            towns_p[p.town] = towns_p.get(p.town, 0) + 1
        for c in clusters:
            towns_c[c.town] = towns_c.get(c.town, 0) + 1

        print("\n--- Providers per town ---")
        for town, count in sorted(towns_p.items()):
            print(f"  {town}: {count}")

        print("--- Clusters per town ---")
        for town, count in sorted(towns_c.items()):
            print(f"  {town}: {count}")

        assert len(towns_p) >= 8
        assert len(towns_c) >= 8
