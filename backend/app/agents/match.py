"""Match agent — ranks providers against a demand cluster.

Fully deterministic, no LLM required.

Scoring formula from ARCHITECTURE.md §6.2:
    Score (0–1) = weighted sum of five factors.

    | Factor       | Weight | Definition                                                      |
    |-------------|--------|------------------------------------------------------------------|
    | Distance    | 0.30   | max(0, 1 - distance_km / radius_km)                             |
    | Cuisine fit | 0.25   | sum(cluster.cuisine_weights[c] for c in provider.cuisines) ≤ 1   |
    | Price fit   | 0.25   | 1 if list_price ≤ ceiling, else max(0, 1-(price-ceil)/ceil)      |
    | Capacity    | 0.15   | min(1, capacity_available / headcount)                           |
    | Rating      | 0.05   | rating / 5                                                       |
"""

from __future__ import annotations

from collections.abc import Mapping

from app.agents.geo import haversine_km
from app.models.domain import DemandCluster, Diet, Provider, ProviderMatch

# Factor weights (must sum to 1.0)
W_DISTANCE = 0.30
W_CUISINE = 0.25
W_PRICE = 0.25
W_CAPACITY = 0.15
W_RATING = 0.05

# Human-readable factor labels for the reason string
_FACTOR_LABELS: dict[str, str] = {
    "distance": "Close by",
    "cuisine_fit": "Matches cuisine preference",
    "price_fit": "Affordable pricing",
    "capacity_fit": "Has available capacity",
    "rating": "Highly rated",
}


# ---------------------------------------------------------------------------
# Individual scoring functions (testable in isolation)
# ---------------------------------------------------------------------------


def score_distance(
    provider_lat: float,
    provider_lon: float,
    cluster_lat: float,
    cluster_lon: float,
    radius_km: float,
) -> float:
    """Distance factor: ``max(0, 1 - distance_km / radius_km)``."""
    dist = haversine_km(provider_lat, provider_lon, cluster_lat, cluster_lon)
    return max(0.0, 1.0 - dist / radius_km)


def score_cuisine_fit(
    provider_cuisines: list[str],
    cluster_cuisine_weights: dict[str, float],
) -> float:
    """Cuisine fit: ``sum(weights for matching cuisines)``, capped at 1."""
    total = sum(cluster_cuisine_weights.get(c, 0.0) for c in provider_cuisines)
    return min(1.0, total)


def score_price_fit(list_price_monthly: float, budget_ceiling: float) -> float:
    """Price fit: 1 if affordable, degrades linearly above ceiling."""
    if budget_ceiling <= 0:
        return 0.0
    if list_price_monthly <= budget_ceiling:
        return 1.0
    return max(0.0, 1.0 - (list_price_monthly - budget_ceiling) / budget_ceiling)


def score_capacity_fit(capacity_available: int, headcount: int) -> float:
    """Capacity fit: ``min(1, available / headcount)``."""
    if headcount <= 0:
        return 1.0
    return min(1.0, capacity_available / headcount)


def score_rating(rating: float) -> float:
    """Rating factor: ``rating / 5``."""
    return rating / 5.0


# ---------------------------------------------------------------------------
# Exclusion checks
# ---------------------------------------------------------------------------


def _has_diet_overlap(provider_diets: list[Diet], cluster_diet_split: Mapping[Diet, float]) -> bool:
    """Return True if the provider offers at least one diet the cluster wants."""
    return any(cluster_diet_split.get(diet, 0.0) > 0.0 for diet in provider_diets)


def _is_excluded(
    provider: Provider,
    cluster: DemandCluster,
    radius_km: float,
) -> bool:
    """Return True if the provider should be excluded from matching."""
    # Not approved
    if provider.status != "approved":
        return True
    # Zero capacity
    if provider.capacity_available <= 0:
        return True
    # No diet overlap
    if not _has_diet_overlap(provider.diet_types, cluster.diet_split):
        return True
    # Outside radius
    dist = haversine_km(provider.lat, provider.lon, cluster.lat, cluster.lon)
    return dist > radius_km


# ---------------------------------------------------------------------------
# Reason builder
# ---------------------------------------------------------------------------


def _build_reason(
    factors: dict[str, float],
    distance_km: float,
    provider: Provider,
    cluster: DemandCluster,
) -> str:
    """Build a plain-language reason from the top two scoring factors."""
    sorted_factors = sorted(factors.items(), key=lambda kv: kv[1], reverse=True)
    parts: list[str] = []

    for name, _value in sorted_factors[:2]:
        label = _FACTOR_LABELS.get(name, name)
        if name == "distance":
            parts.append(f"{label} ({distance_km:.1f} km)")
        elif name == "cuisine_fit":
            matching = [c for c in provider.cuisines if c in cluster.cuisine_weights]
            cuisine_str = " and ".join(matching) if matching else "matching"
            parts.append(f"Matches {cuisine_str} preference")
        elif name == "price_fit":
            parts.append(f"{label} (₹{provider.list_price_monthly:.0f}/mo)")
        else:
            parts.append(label)

    return " and ".join(parts) if parts else "Matched"


# ---------------------------------------------------------------------------
# Main agent function
# ---------------------------------------------------------------------------


def run_match_agent(
    cluster: DemandCluster,
    providers: list[Provider],
    top_n: int = 5,
    radius_km: float = 5.0,
) -> list[ProviderMatch]:
    """Score and rank providers against a demand cluster.

    Returns the top-N providers sorted by score (descending), with
    per-factor breakdown and a plain-language reason.  Ties are broken
    by provider ID for stable ordering.

    Raises no exceptions — returns an empty list when no providers qualify.
    """
    matches: list[ProviderMatch] = []

    for provider in providers:
        if _is_excluded(provider, cluster, radius_km):
            continue

        # Compute each factor
        dist_km = haversine_km(provider.lat, provider.lon, cluster.lat, cluster.lon)
        f_distance = score_distance(provider.lat, provider.lon, cluster.lat, cluster.lon, radius_km)
        f_cuisine = score_cuisine_fit(provider.cuisines, cluster.cuisine_weights)
        f_price = score_price_fit(provider.list_price_monthly, cluster.budget_ceiling_monthly)
        f_capacity = score_capacity_fit(provider.capacity_available, cluster.headcount)
        f_rating = score_rating(provider.rating)

        # Weighted total
        total = (
            W_DISTANCE * f_distance
            + W_CUISINE * f_cuisine
            + W_PRICE * f_price
            + W_CAPACITY * f_capacity
            + W_RATING * f_rating
        )

        factors = {
            "distance": round(f_distance, 4),
            "cuisine_fit": round(f_cuisine, 4),
            "price_fit": round(f_price, 4),
            "capacity_fit": round(f_capacity, 4),
            "rating": round(f_rating, 4),
        }

        reason = _build_reason(factors, dist_km, provider, cluster)

        matches.append(
            ProviderMatch(
                provider_id=provider.id,
                score=round(total, 4),
                factors=factors,
                distance_km=round(dist_km, 2),
                reason=reason,
            )
        )

    # Sort by score desc, then by provider_id for tie-breaking stability
    matches.sort(key=lambda m: (-m.score, m.provider_id))

    return matches[:top_n]
