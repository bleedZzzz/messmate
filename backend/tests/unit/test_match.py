"""Tests for the Match agent — scoring factors, exclusions, ranking.

Every scoring factor is tested in isolation with hand-computed expected values.
"""

import pytest

from app.agents.match import (
    W_CAPACITY,
    W_CUISINE,
    W_DISTANCE,
    W_PRICE,
    W_RATING,
    run_match_agent,
    score_capacity_fit,
    score_cuisine_fit,
    score_distance,
    score_price_fit,
    score_rating,
)
from app.models.domain import DemandCluster, Dish, Provider, ProviderMatch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_cluster(
    lat: float = 22.500,
    lon: float = 88.370,
    headcount: int = 40,
    budget: float = 3000.0,
    cuisine_weights: dict[str, float] | None = None,
    diet_split: dict[str, float] | None = None,
) -> DemandCluster:
    return DemandCluster(
        id="cluster-1",
        town="Kolkata",
        area="Jadavpur",
        lat=lat,
        lon=lon,
        headcount=headcount,
        budget_ceiling_monthly=budget,
        cuisine_weights=cuisine_weights or {"bengali": 0.6, "north_indian": 0.3, "chinese": 0.1},
        diet_split=diet_split or {"veg": 0.4, "non_veg": 0.4, "egg": 0.2},
        flexibility=0.3,
    )


def _make_provider(
    id: str = "p1",
    lat: float = 22.502,
    lon: float = 88.372,
    cuisines: list[str] | None = None,
    diet_types: list[str] | None = None,
    capacity_total: int = 50,
    capacity_available: int = 20,
    list_price: float = 2800.0,
    cost_per_meal: float = 30.0,
    rating: float = 4.0,
    status: str = "approved",
) -> Provider:
    dishes = [
        Dish(
            id=f"{id}-d1",
            name="Dal",
            slot="lunch",
            diet="veg",
            cuisine="bengali",
            main_item="dal",
            cost_tier=1,
        ),
        Dish(
            id=f"{id}-d2",
            name="Rice",
            slot="dinner",
            diet="veg",
            cuisine="bengali",
            main_item="vegetables",
            cost_tier=1,
        ),
    ]
    return Provider(
        id=id,
        name="Test Mess",
        town="Kolkata",
        area="Jadavpur",
        lat=lat,
        lon=lon,
        cuisines=cuisines or ["bengali"],
        diet_types=diet_types or ["veg", "non_veg"],
        capacity_total=capacity_total,
        capacity_available=capacity_available,
        list_price_monthly=list_price,
        cost_per_meal=cost_per_meal,
        min_margin=0.15,
        flexibility=0.3,
        rating=rating,
        dishes=dishes,
        phone="+91 00000 01234",
        status=status,  # type: ignore[arg-type]
    )


# ---------------------------------------------------------------------------
# Factor tests (isolated, hand-computed)
# ---------------------------------------------------------------------------


class TestScoreDistance:
    def test_same_location(self) -> None:
        """Provider at exact cluster location → score = 1.0."""
        assert score_distance(22.5, 88.4, 22.5, 88.4, radius_km=5.0) == 1.0

    def test_at_radius_boundary(self) -> None:
        """Provider at exactly the radius → score ≈ 0.0."""
        # ~5 km away: 22.5 to 22.545 is about 5 km at this latitude
        s = score_distance(22.5, 88.4, 22.545, 88.4, radius_km=5.0)
        assert s == pytest.approx(0.0, abs=0.05)

    def test_beyond_radius(self) -> None:
        """Provider far beyond radius → score = 0.0."""
        s = score_distance(22.5, 88.4, 23.5, 87.3, radius_km=5.0)
        assert s == 0.0

    def test_half_radius(self) -> None:
        """Provider at half the radius → score ≈ 0.5."""
        # ~2.5 km at this latitude is roughly 0.0225 degrees
        s = score_distance(22.5, 88.4, 22.5225, 88.4, radius_km=5.0)
        assert 0.4 < s < 0.6


class TestScoreCuisineFit:
    def test_perfect_match(self) -> None:
        """Provider offers the only cuisine → sum of weights for it."""
        s = score_cuisine_fit(["bengali"], {"bengali": 0.6, "north_indian": 0.4})
        assert s == pytest.approx(0.6)

    def test_multiple_match(self) -> None:
        """Provider offers both → sum capped at 1.0."""
        s = score_cuisine_fit(["bengali", "north_indian"], {"bengali": 0.6, "north_indian": 0.4})
        assert s == pytest.approx(1.0)

    def test_no_match(self) -> None:
        """Provider cuisine not in cluster weights → 0.0."""
        s = score_cuisine_fit(["south_indian"], {"bengali": 0.6, "north_indian": 0.4})
        assert s == 0.0

    def test_capped_at_one(self) -> None:
        s = score_cuisine_fit(
            ["bengali", "north_indian", "chinese"],
            {"bengali": 0.5, "north_indian": 0.4, "chinese": 0.3},
        )
        assert s == 1.0  # 0.5+0.4+0.3=1.2 → capped to 1.0


class TestScorePriceFit:
    def test_affordable(self) -> None:
        """Price ≤ ceiling → 1.0."""
        assert score_price_fit(2800, 3000) == 1.0

    def test_exactly_at_ceiling(self) -> None:
        """Price == ceiling → 1.0."""
        assert score_price_fit(3000, 3000) == 1.0

    def test_above_ceiling(self) -> None:
        """Price 50% above ceiling → max(0, 1 - 0.5) = 0.5."""
        s = score_price_fit(4500, 3000)
        assert s == pytest.approx(0.5)

    def test_far_above_ceiling(self) -> None:
        """Price ≥ 2× ceiling → 0.0."""
        assert score_price_fit(6000, 3000) == 0.0

    def test_zero_ceiling(self) -> None:
        assert score_price_fit(1000, 0) == 0.0


class TestScoreCapacityFit:
    def test_more_than_enough(self) -> None:
        """Capacity ≥ headcount → 1.0."""
        assert score_capacity_fit(50, 40) == 1.0

    def test_exact_match(self) -> None:
        assert score_capacity_fit(40, 40) == 1.0

    def test_partial(self) -> None:
        """20 / 40 = 0.5."""
        assert score_capacity_fit(20, 40) == pytest.approx(0.5)

    def test_zero_headcount(self) -> None:
        assert score_capacity_fit(10, 0) == 1.0


class TestScoreRating:
    def test_perfect(self) -> None:
        assert score_rating(5.0) == 1.0

    def test_four(self) -> None:
        assert score_rating(4.0) == pytest.approx(0.8)

    def test_zero(self) -> None:
        assert score_rating(0.0) == 0.0


class TestWeightsSum:
    def test_weights_sum_to_one(self) -> None:
        total = W_DISTANCE + W_CUISINE + W_PRICE + W_CAPACITY + W_RATING
        assert total == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Exclusion tests
# ---------------------------------------------------------------------------


class TestExclusions:
    def test_pending_provider_excluded(self) -> None:
        cluster = _make_cluster()
        p = _make_provider(status="pending")
        result = run_match_agent(cluster, [p])
        assert len(result) == 0

    def test_zero_capacity_excluded(self) -> None:
        cluster = _make_cluster()
        p = _make_provider(capacity_available=0)
        result = run_match_agent(cluster, [p])
        assert len(result) == 0

    def test_no_diet_overlap_excluded(self) -> None:
        cluster = _make_cluster(diet_split={"veg": 1.0})
        p = _make_provider(diet_types=["non_veg"])  # cluster only wants veg
        result = run_match_agent(cluster, [p])
        assert len(result) == 0

    def test_outside_radius_excluded(self) -> None:
        cluster = _make_cluster(lat=22.500, lon=88.370)
        p = _make_provider(lat=23.500, lon=87.300)  # ~152 km away
        result = run_match_agent(cluster, [p], radius_km=5.0)
        assert len(result) == 0

    def test_approved_within_radius_included(self) -> None:
        cluster = _make_cluster()
        p = _make_provider()  # close, approved, has capacity and diet overlap
        result = run_match_agent(cluster, [p])
        assert len(result) == 1


# ---------------------------------------------------------------------------
# Ranking and scoring
# ---------------------------------------------------------------------------


class TestRanking:
    def test_higher_score_ranked_first(self) -> None:
        cluster = _make_cluster()
        p_good = _make_provider(id="good", rating=5.0, list_price=2000)
        p_bad = _make_provider(id="bad", rating=2.0, list_price=3500)
        result = run_match_agent(cluster, [p_bad, p_good])
        assert result[0].provider_id == "good"
        assert result[0].score >= result[1].score

    def test_top_n_limits_results(self) -> None:
        cluster = _make_cluster()
        providers = [_make_provider(id=f"p{i}") for i in range(10)]
        result = run_match_agent(cluster, providers, top_n=3)
        assert len(result) == 3

    def test_stable_ordering_on_ties(self) -> None:
        """Providers with identical scores are sorted by ID."""
        cluster = _make_cluster()
        p_b = _make_provider(id="p-beta")
        p_a = _make_provider(id="p-alpha")
        result = run_match_agent(cluster, [p_b, p_a])
        # Same score → alphabetical by ID
        assert result[0].provider_id == "p-alpha"
        assert result[1].provider_id == "p-beta"

    def test_empty_providers_returns_empty(self) -> None:
        cluster = _make_cluster()
        result = run_match_agent(cluster, [])
        assert result == []


class TestMatchOutput:
    def test_output_has_all_fields(self) -> None:
        cluster = _make_cluster()
        p = _make_provider()
        result = run_match_agent(cluster, [p])
        assert len(result) == 1
        m = result[0]
        assert isinstance(m, ProviderMatch)
        assert 0 <= m.score <= 1
        assert m.distance_km >= 0
        assert "distance" in m.factors
        assert "cuisine_fit" in m.factors
        assert "price_fit" in m.factors
        assert "capacity_fit" in m.factors
        assert "rating" in m.factors
        assert len(m.reason) > 0

    def test_score_within_bounds(self) -> None:
        cluster = _make_cluster()
        providers = [_make_provider(id=f"p{i}", rating=float(i)) for i in range(1, 6)]
        result = run_match_agent(cluster, providers, top_n=10)
        for m in result:
            assert 0 <= m.score <= 1
            for factor_value in m.factors.values():
                assert 0 <= factor_value <= 1


class TestHandComputedScore:
    """Verify an end-to-end score with hand-computed values."""

    def test_known_score(self) -> None:
        cluster = _make_cluster(
            lat=22.500,
            lon=88.370,
            headcount=40,
            budget=3000.0,
            cuisine_weights={"bengali": 0.6, "north_indian": 0.4},
        )
        # Provider is AT the cluster location
        p = _make_provider(
            lat=22.500,
            lon=88.370,
            cuisines=["bengali"],
            capacity_available=40,
            list_price=3000.0,
            rating=4.0,
        )
        result = run_match_agent(cluster, [p], radius_km=5.0)
        assert len(result) == 1
        m = result[0]

        # Hand-computed:
        # distance = 0 km → factor = 1.0
        # cuisine_fit = 0.6 (only bengali)
        # price_fit = 1.0 (3000 <= 3000)
        # capacity_fit = min(1, 40/40) = 1.0
        # rating = 4/5 = 0.8
        #
        # score = 0.30*1.0 + 0.25*0.6 + 0.25*1.0 + 0.15*1.0 + 0.05*0.8
        #       = 0.30 + 0.15 + 0.25 + 0.15 + 0.04
        #       = 0.89
        assert m.score == pytest.approx(0.89, abs=0.01)
        assert m.factors["distance"] == pytest.approx(1.0)
        assert m.factors["cuisine_fit"] == pytest.approx(0.6)
        assert m.factors["price_fit"] == pytest.approx(1.0)
        assert m.factors["capacity_fit"] == pytest.approx(1.0)
        assert m.factors["rating"] == pytest.approx(0.8)
