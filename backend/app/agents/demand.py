"""Demand agent — selects the best-fit demand cluster for a search.

Fully deterministic, no LLM required.

Data source is behind a ``ClusterSource`` protocol so a real-data provider
can be plugged in later without touching the agent logic.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel, Field

from app.agents.geo import haversine_km
from app.models.domain import DemandCluster, Diet

# ---------------------------------------------------------------------------
# ClusterSource interface (FR-3)
# ---------------------------------------------------------------------------


@runtime_checkable
class ClusterSource(Protocol):
    """Pluggable data source for demand clusters."""

    def get_all(self) -> list[DemandCluster]:
        """Return every cluster in the data source."""
        ...

    def get_by_id(self, cluster_id: str) -> DemandCluster | None:
        """Return a single cluster by ID, or ``None``."""
        ...


# ---------------------------------------------------------------------------
# Input / output models
# ---------------------------------------------------------------------------


class DemandRequest(BaseModel):
    """Input for the Demand agent."""

    area: str | None = None
    lat: float | None = None
    lon: float | None = None
    radius_km: float = Field(default=5.0, gt=0)
    diet: Diet | None = None
    budget_max: float | None = None
    cluster_id: str | None = None


class DemandResult(BaseModel):
    """Output of the Demand agent."""

    clusters: list[DemandCluster]
    selected: DemandCluster


# ---------------------------------------------------------------------------
# Agent
# ---------------------------------------------------------------------------


def run_demand_agent(
    request: DemandRequest,
    source: ClusterSource,
) -> DemandResult:
    """Find and rank demand clusters, then select the best one.

    Selection logic (per ARCHITECTURE.md §6.1):
    - If ``cluster_id`` is given and found, select it directly.
    - Otherwise filter by area name match **or** by lat/lon + radius (haversine).
    - Rank by a combination of headcount (weight) and proximity.
    - Select the top-ranked cluster.

    Raises ``ValueError`` if no clusters match the request.
    """
    # --- Short-circuit: explicit cluster requested ---
    if request.cluster_id:
        cluster = source.get_by_id(request.cluster_id)
        if cluster is None:
            raise ValueError(f"Cluster '{request.cluster_id}' not found")
        return DemandResult(clusters=[cluster], selected=cluster)

    all_clusters = source.get_all()

    # --- Filter ---
    if request.area:
        # Match on town or area name (case-insensitive substring)
        area_lower = request.area.lower()
        filtered = [
            c for c in all_clusters if area_lower in c.area.lower() or area_lower in c.town.lower()
        ]
    elif request.lat is not None and request.lon is not None:
        # Filter by haversine radius
        filtered = [
            c
            for c in all_clusters
            if haversine_km(request.lat, request.lon, c.lat, c.lon) <= request.radius_km
        ]
    else:
        filtered = list(all_clusters)

    # --- Optional diet / budget hints ---
    if request.diet:
        diet_key = request.diet
        filtered = [c for c in filtered if diet_key in c.diet_split]

    if request.budget_max is not None:
        filtered = [c for c in filtered if c.budget_ceiling_monthly <= request.budget_max]

    if not filtered:
        raise ValueError("No demand clusters match the given search criteria")

    # --- Rank: headcount × proximity score ---
    def _rank_key(c: DemandCluster) -> float:
        if request.lat is not None and request.lon is not None:
            dist = haversine_km(request.lat, request.lon, c.lat, c.lon)
            proximity = max(0.0, 1.0 - dist / request.radius_km)
        else:
            proximity = 1.0  # area-based search — no proximity penalty
        return c.headcount * (0.6 + 0.4 * proximity)

    ranked = sorted(filtered, key=_rank_key, reverse=True)

    return DemandResult(clusters=ranked, selected=ranked[0])
