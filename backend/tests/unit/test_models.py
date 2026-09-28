"""Tests for Pydantic domain models."""

import pytest
from pydantic import ValidationError

from app.models.domain import (
    DayMenu,
    DemandCluster,
    Dish,
    MealPick,
    MenuPlan,
    NegotiationResult,
    NegotiationRound,
    Provider,
    ProviderMatch,
    TraceStep,
)


class TestDish:
    def test_valid_dish(self) -> None:
        dish = Dish(
            id="d1",
            name="Dal Tadka",
            slot="lunch",
            diet="veg",
            cuisine="north_indian",
            main_item="dal",
            cost_tier=1,
        )
        assert dish.slot == "lunch"
        assert dish.diet == "veg"

    def test_invalid_slot_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Dish(
                id="d1",
                name="Test",
                slot="breakfast",  # type: ignore[arg-type]
                diet="veg",
                cuisine="test",
                main_item="test",
                cost_tier=1,
            )

    def test_invalid_diet_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Dish(
                id="d1",
                name="Test",
                slot="lunch",
                diet="jain",  # type: ignore[arg-type]
                cuisine="test",
                main_item="test",
                cost_tier=1,
            )

    def test_invalid_cost_tier_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Dish(
                id="d1",
                name="Test",
                slot="lunch",
                diet="veg",
                cuisine="test",
                main_item="test",
                cost_tier=5,  # type: ignore[arg-type]
            )


class TestProvider:
    def _minimal_provider(self, **overrides) -> Provider:  # type: ignore[no-untyped-def]
        defaults = dict(
            id="p1",
            name="Test Mess",
            town="Kolkata",
            area="Jadavpur",
            lat=22.5,
            lon=88.4,
            cuisines=["bengali"],
            diet_types=["veg"],
            capacity_total=50,
            capacity_available=10,
            list_price_monthly=3000,
            cost_per_meal=30,
            min_margin=0.15,
            flexibility=0.3,
            rating=4.0,
            dishes=[],
        )
        defaults.update(overrides)
        return Provider(**defaults)

    def test_valid_provider(self) -> None:
        p = self._minimal_provider()
        assert p.status == "approved"  # default
        assert p.phone is None  # default

    def test_min_margin_bounds(self) -> None:
        with pytest.raises(ValidationError):
            self._minimal_provider(min_margin=1.5)
        with pytest.raises(ValidationError):
            self._minimal_provider(min_margin=-0.1)

    def test_flexibility_bounds(self) -> None:
        with pytest.raises(ValidationError):
            self._minimal_provider(flexibility=0.0)  # must be > 0
        with pytest.raises(ValidationError):
            self._minimal_provider(flexibility=1.5)

    def test_rating_bounds(self) -> None:
        with pytest.raises(ValidationError):
            self._minimal_provider(rating=-1)
        with pytest.raises(ValidationError):
            self._minimal_provider(rating=6)


class TestDemandCluster:
    def test_valid_cluster(self) -> None:
        c = DemandCluster(
            id="c1",
            town="Kolkata",
            area="Jadavpur",
            lat=22.5,
            lon=88.4,
            headcount=30,
            budget_ceiling_monthly=3000,
            cuisine_weights={"bengali": 0.7, "north_indian": 0.3},
            diet_split={"veg": 0.5, "non_veg": 0.3, "egg": 0.2},
            flexibility=0.4,
        )
        assert c.headcount == 30

    def test_flexibility_bounds(self) -> None:
        with pytest.raises(ValidationError):
            DemandCluster(
                id="c1",
                town="T",
                area="A",
                lat=22.0,
                lon=88.0,
                headcount=10,
                budget_ceiling_monthly=3000,
                cuisine_weights={},
                diet_split={},
                flexibility=0.0,
            )


class TestOutputModels:
    def test_provider_match(self) -> None:
        m = ProviderMatch(
            provider_id="p1",
            score=0.85,
            factors={"distance": 0.9, "cuisine": 0.8},
            distance_km=1.2,
            reason="Close by and matches Bengali preference",
        )
        assert m.score == 0.85

    def test_menu_plan(self) -> None:
        plan = MenuPlan(
            provider_id="p1",
            cluster_id="c1",
            days=[
                DayMenu(
                    day=1,
                    lunch=MealPick(dish_id="d1", name="Dal"),
                    dinner=MealPick(dish_id="d2", name="Roti"),
                )
            ],
            rationale="test",
            source="fallback",
        )
        assert plan.source == "fallback"
        assert len(plan.days) == 1

    def test_negotiation_result(self) -> None:
        result = NegotiationResult(
            status="deal",
            final_price=2800.0,
            floor=2500.0,
            ceiling=3000.0,
            volume_discount=0.05,
            rounds=[NegotiationRound(round=1, provider_ask=3000, cluster_bid=2600)],
            note="Good deal",
        )
        assert result.final_price == 2800.0

    def test_trace_step(self) -> None:
        step = TraceStep(
            agent="match",
            started_ms=1000,
            duration_ms=50,
            used_llm=False,
            fallback_used=False,
        )
        assert step.error is None
