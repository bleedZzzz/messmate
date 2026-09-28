"""Tests for the Demand agent and ClusterSource."""

import pytest

from app.agents.demand import (
    ClusterSource,
    DemandRequest,
    run_demand_agent,
)
from app.agents.geo import haversine_km
from app.models.domain import DemandCluster

# ---------------------------------------------------------------------------
# Fake ClusterSource for tests
# ---------------------------------------------------------------------------


class FakeClusterSource:
    """In-memory cluster source for unit tests."""

    def __init__(self, clusters: list[DemandCluster]) -> None:
        self._clusters = clusters

    def get_all(self) -> list[DemandCluster]:
        return list(self._clusters)

    def get_by_id(self, cluster_id: str) -> DemandCluster | None:
        for c in self._clusters:
            if c.id == cluster_id:
                return c
        return None


def _make_cluster(
    id: str = "c1",
    town: str = "Kolkata",
    area: str = "Jadavpur",
    lat: float = 22.499,
    lon: float = 88.371,
    headcount: int = 40,
    budget: float = 3000.0,
    flexibility: float = 0.3,
) -> DemandCluster:
    return DemandCluster(
        id=id,
        town=town,
        area=area,
        lat=lat,
        lon=lon,
        headcount=headcount,
        budget_ceiling_monthly=budget,
        cuisine_weights={"bengali": 0.6, "north_indian": 0.3, "chinese": 0.1},
        diet_split={"veg": 0.4, "non_veg": 0.4, "egg": 0.2},
        flexibility=flexibility,
    )


# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


class TestClusterSourceProtocol:
    def test_fake_source_implements_protocol(self) -> None:
        source = FakeClusterSource([])
        assert isinstance(source, ClusterSource)


# ---------------------------------------------------------------------------
# Haversine
# ---------------------------------------------------------------------------


class TestHaversine:
    def test_same_point_is_zero(self) -> None:
        assert haversine_km(22.5, 88.4, 22.5, 88.4) == 0.0

    def test_known_distance_kolkata_durgapur(self) -> None:
        """Kolkata (22.5726, 88.3639) → Durgapur (23.5204, 87.3119).

        Expected ≈ 152 km (straight line).
        """
        dist = haversine_km(22.5726, 88.3639, 23.5204, 87.3119)
        assert 145 < dist < 160, f"Expected ~152 km, got {dist:.1f}"

    def test_known_distance_kolkata_howrah(self) -> None:
        """Kolkata (22.5726, 88.3639) → Howrah (22.5958, 88.2636).

        Expected ≈ 10–12 km.
        """
        dist = haversine_km(22.5726, 88.3639, 22.5958, 88.2636)
        assert 9 < dist < 13, f"Expected ~11 km, got {dist:.1f}"

    def test_symmetry(self) -> None:
        d1 = haversine_km(22.5, 88.4, 23.5, 87.3)
        d2 = haversine_km(23.5, 87.3, 22.5, 88.4)
        assert abs(d1 - d2) < 0.001


# ---------------------------------------------------------------------------
# Demand agent — cluster selection
# ---------------------------------------------------------------------------


class TestDemandAgentClusterId:
    """When cluster_id is specified, select it directly."""

    def test_selects_by_id(self) -> None:
        c1 = _make_cluster(id="c1")
        c2 = _make_cluster(id="c2", area="Salt Lake")
        source = FakeClusterSource([c1, c2])

        result = run_demand_agent(DemandRequest(cluster_id="c2"), source)
        assert result.selected.id == "c2"
        assert len(result.clusters) == 1

    def test_raises_on_missing_id(self) -> None:
        source = FakeClusterSource([_make_cluster()])
        with pytest.raises(ValueError, match="not found"):
            run_demand_agent(DemandRequest(cluster_id="missing"), source)


class TestDemandAgentAreaFilter:
    """Filter by area/town name substring."""

    def test_filters_by_area(self) -> None:
        c1 = _make_cluster(id="c1", town="Kolkata", area="Jadavpur")
        c2 = _make_cluster(id="c2", town="Durgapur", area="NIT Campus")
        source = FakeClusterSource([c1, c2])

        result = run_demand_agent(DemandRequest(area="Jadavpur"), source)
        assert all(
            "jadavpur" in c.area.lower() or "jadavpur" in c.town.lower() for c in result.clusters
        )

    def test_filters_by_town_name(self) -> None:
        c1 = _make_cluster(id="c1", town="Kolkata", area="Jadavpur")
        c2 = _make_cluster(id="c2", town="Durgapur", area="NIT Campus")
        source = FakeClusterSource([c1, c2])

        result = run_demand_agent(DemandRequest(area="Kolkata"), source)
        assert result.selected.town == "Kolkata"

    def test_case_insensitive(self) -> None:
        c1 = _make_cluster(id="c1", area="Jadavpur")
        source = FakeClusterSource([c1])

        result = run_demand_agent(DemandRequest(area="jadavpur"), source)
        assert result.selected.id == "c1"


class TestDemandAgentLatLonFilter:
    """Filter by lat/lon + radius using haversine."""

    def test_filters_by_radius(self) -> None:
        c_near = _make_cluster(id="near", lat=22.500, lon=88.370)
        c_far = _make_cluster(id="far", lat=23.500, lon=87.300)  # ~152 km away
        source = FakeClusterSource([c_near, c_far])

        result = run_demand_agent(
            DemandRequest(lat=22.500, lon=88.370, radius_km=5.0),
            source,
        )
        assert len(result.clusters) == 1
        assert result.selected.id == "near"

    def test_no_match_raises(self) -> None:
        c_far = _make_cluster(id="far", lat=23.500, lon=87.300)
        source = FakeClusterSource([c_far])

        with pytest.raises(ValueError, match="No demand clusters"):
            run_demand_agent(
                DemandRequest(lat=22.500, lon=88.370, radius_km=1.0),
                source,
            )


class TestDemandAgentRanking:
    """Ranking by headcount and proximity."""

    def test_ranks_by_headcount_for_area(self) -> None:
        c_small = _make_cluster(id="small", area="Jadavpur", headcount=10)
        c_big = _make_cluster(id="big", area="Jadavpur", headcount=60)
        source = FakeClusterSource([c_small, c_big])

        result = run_demand_agent(DemandRequest(area="Jadavpur"), source)
        assert result.selected.id == "big"  # higher headcount wins
        assert result.clusters[0].id == "big"

    def test_proximity_affects_ranking(self) -> None:
        c_near = _make_cluster(id="near", lat=22.500, lon=88.370, headcount=30)
        c_far = _make_cluster(id="far", lat=22.530, lon=88.400, headcount=30)
        source = FakeClusterSource([c_near, c_far])

        result = run_demand_agent(
            DemandRequest(lat=22.500, lon=88.370, radius_km=10.0),
            source,
        )
        # Same headcount, but c_near is closer → higher score
        assert result.selected.id == "near"


class TestDemandAgentOptionalFilters:
    """Diet and budget hints."""

    def test_diet_filter(self) -> None:
        c1 = _make_cluster(id="c1")  # diet_split includes "veg"
        source = FakeClusterSource([c1])

        result = run_demand_agent(DemandRequest(diet="veg"), source)
        assert result.selected.id == "c1"

    def test_budget_filter(self) -> None:
        c_cheap = _make_cluster(id="cheap", budget=2000)
        c_expensive = _make_cluster(id="expensive", budget=3500)
        source = FakeClusterSource([c_cheap, c_expensive])

        result = run_demand_agent(DemandRequest(budget_max=2500), source)
        assert all(c.budget_ceiling_monthly <= 2500 for c in result.clusters)

    def test_all_filtered_out_raises(self) -> None:
        c1 = _make_cluster(id="c1", budget=3000)
        source = FakeClusterSource([c1])

        with pytest.raises(ValueError, match="No demand clusters"):
            run_demand_agent(DemandRequest(budget_max=1000), source)


class TestDemandAgentEmptySource:
    def test_empty_source_raises(self) -> None:
        source = FakeClusterSource([])
        with pytest.raises(ValueError, match="No demand clusters"):
            run_demand_agent(DemandRequest(), source)
