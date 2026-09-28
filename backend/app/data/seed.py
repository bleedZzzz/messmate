"""Seed the database with synthetic data.

Idempotent: does nothing when data already exists.
"""

import structlog
from sqlalchemy.orm import Session

from app.data.synthetic_generator import generate_clusters, generate_providers
from app.db.repositories import count_clusters, count_providers, insert_cluster, insert_provider

logger = structlog.get_logger()


def seed_database(session: Session, seed: int = 42) -> dict[str, int]:
    """Generate and insert synthetic data if tables are empty.

    Returns a dict with counts of providers and clusters inserted (0 if skipped).
    """
    existing_providers = count_providers(session)
    existing_clusters = count_clusters(session)

    if existing_providers > 0 or existing_clusters > 0:
        logger.info(
            "seed_skipped",
            providers=existing_providers,
            clusters=existing_clusters,
            reason="data already exists",
        )
        return {"providers": 0, "clusters": 0}

    providers = generate_providers(seed=seed)
    clusters = generate_clusters(seed=seed)

    for provider in providers:
        insert_provider(session, provider, consent=True)
    for cluster in clusters:
        insert_cluster(session, cluster)

    session.commit()

    logger.info(
        "seed_complete",
        providers=len(providers),
        clusters=len(clusters),
    )
    return {"providers": len(providers), "clusters": len(clusters)}
