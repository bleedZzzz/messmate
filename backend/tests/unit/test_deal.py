"""Unit tests and Hypothesis property tests for the Deal agent (negotiation)."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.agents.deal import DealAgent, compute_volume_discount, negotiate, run_deal_agent
from app.llm.base import FakeProvider, NoneProvider
from app.models.domain import DemandCluster, Dish, Provider


def _make_provider(
    cost_per_meal: float = 30.0,
    min_margin: float = 0.15,
    list_price_monthly: float = 2800.0,
    flexibility: float = 0.50,
) -> Provider:
    """Helper to create test provider with specific pricing parameters."""
    return Provider(
        id="test-prov",
        name="Test Mess",
        town="Kolkata",
        area="Jadavpur",
        lat=22.49,
        lon=88.37,
        cuisines=["bengali"],
        diet_types=["veg"],
        capacity_total=50,
        capacity_available=25,
        list_price_monthly=list_price_monthly,
        cost_per_meal=cost_per_meal,
        min_margin=min_margin,
        flexibility=flexibility,
        rating=4.5,
        dishes=[
            Dish(
                id=f"d-{i}",
                name=f"Dish {i}",
                slot="lunch",
                diet="veg",
                cuisine="bengali",
                main_item="dal",
                cost_tier=1,
            )
            for i in range(10)
        ],
    )


def _make_cluster(
    budget_ceiling_monthly: float = 3000.0,
    headcount: int = 20,
    flexibility: float = 0.50,
) -> DemandCluster:
    """Helper to create test cluster with specific budget/headcount."""
    return DemandCluster(
        id="test-cluster",
        town="Kolkata",
        area="Jadavpur",
        lat=22.49,
        lon=88.37,
        headcount=headcount,
        budget_ceiling_monthly=budget_ceiling_monthly,
        cuisine_weights={"bengali": 1.0},
        diet_split={"veg": 1.0, "non_veg": 0.0, "egg": 0.0},
        flexibility=flexibility,
    )


# ---------------------------------------------------------------------------
# Volume Discount Boundary Tests
# ---------------------------------------------------------------------------


def test_volume_discount_boundaries():
    """Verify exact volume discount steps at 9, 10, 24, 25 members."""
    # Under 10 members -> 0%
    assert compute_volume_discount(1) == 0.00
    assert compute_volume_discount(9) == 0.00

    # 10 to 24 members -> 5%
    assert compute_volume_discount(10) == 0.05
    assert compute_volume_discount(15) == 0.05
    assert compute_volume_discount(24) == 0.05

    # 25 and above -> 10%
    assert compute_volume_discount(25) == 0.10
    assert compute_volume_discount(50) == 0.10
    assert compute_volume_discount(100) == 0.10


# ---------------------------------------------------------------------------
# Hand-Built Examples for Each Status
# ---------------------------------------------------------------------------


def test_status_no_deal_when_floor_exceeds_ceiling():
    """Hand-built example reaching status='no_deal'.

    Provider: cost 50 * 60 * 1.20 = floor ₹3,600.
    Cluster: ceiling ₹3,000.
    Since floor (3,600) > ceiling (3,000), result must be no_deal.
    """
    provider = _make_provider(cost_per_meal=50.0, min_margin=0.20)
    cluster = _make_cluster(budget_ceiling_monthly=3000.0)

    result = negotiate(provider, cluster)

    assert result.status == "no_deal"
    assert result.final_price is None
    assert result.floor == 3600.0
    assert result.ceiling == 3000.0
    assert result.rounds == []
    assert "Unable to reach agreement" in result.note
    assert "fewer meals per week" in result.note or "cheaper" in result.note


def test_status_deal_when_bids_meet():
    """Hand-built example reaching status='deal'.

    Provider: list price 2,500, floor 2,000, flexibility 0.6.
    Cluster: ceiling 3,200, opening bid = 3,200 * 0.8 = 2,560.
    Headcount: 25 -> discount 10% -> ask = max(2000, 2500 * 0.9) = 2,250.
    Round 1: bid (2,560) >= ask (2,250) -> immediate deal!
    """
    provider = _make_provider(
        cost_per_meal=25.0, min_margin=0.3333333333, list_price_monthly=2500.0
    )
    # floor = 25 * 60 * 1.333333 = ~2000.0
    cluster = _make_cluster(budget_ceiling_monthly=3200.0, headcount=25)

    result = negotiate(provider, cluster)

    assert result.status == "deal"
    assert result.final_price is not None
    assert result.floor <= result.final_price <= result.ceiling
    assert len(result.rounds) == 1
    assert result.rounds[0].cluster_bid >= result.rounds[0].provider_ask
    assert result.final_price == pytest.approx((2250.0 + 2560.0) / 2.0, abs=1.0)
    assert "Deal agreed in round 1" in result.note


def test_status_compromise_when_rounds_exhausted():
    """Hand-built example reaching status='compromise'.

    Low flexibilities ensure bid and ask never meet within 5 rounds.
    Provider: floor 2,000, list 3,000, flexibility 0.01.
    Cluster: ceiling 2,500, flexibility 0.01 (opening bid: 2,000).
    """
    provider = _make_provider(
        cost_per_meal=25.0, min_margin=0.3333333333, list_price_monthly=3000.0, flexibility=0.01
    )
    cluster = _make_cluster(budget_ceiling_monthly=2500.0, headcount=5, flexibility=0.01)

    result = negotiate(provider, cluster, max_rounds=5)

    assert result.status == "compromise"
    assert result.final_price is not None
    assert result.floor <= result.final_price <= result.ceiling
    assert len(result.rounds) == 5
    assert "Compromise reached after 5 rounds" in result.note


# ---------------------------------------------------------------------------
# Monotonicity & Invariants
# ---------------------------------------------------------------------------


def test_transcript_monotonicity():
    """Verify that provider ask never increases and cluster bid never decreases."""
    provider = _make_provider(
        cost_per_meal=25.0, min_margin=0.20, list_price_monthly=3200.0, flexibility=0.15
    )
    cluster = _make_cluster(budget_ceiling_monthly=3000.0, headcount=15, flexibility=0.15)

    result = negotiate(provider, cluster, max_rounds=5)

    assert len(result.rounds) >= 2
    for i in range(len(result.rounds) - 1):
        r_current = result.rounds[i]
        r_next = result.rounds[i + 1]

        # Ask never increases
        assert r_next.provider_ask <= r_current.provider_ask + 1e-6
        # Bid never decreases
        assert r_next.cluster_bid >= r_current.cluster_bid - 1e-6


# ---------------------------------------------------------------------------
# DealAgent Class & LLM Integration Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_deal_agent_with_none_provider():
    """DealAgent defaults to template note when LLM is NoneProvider."""
    provider = _make_provider()
    cluster = _make_cluster()

    agent = DealAgent(llm_provider=NoneProvider())
    result = await agent.run(provider, cluster)

    assert result.status in ("deal", "compromise")
    assert result.final_price is not None
    assert "₹" in result.note


@pytest.mark.asyncio
async def test_deal_agent_with_llm_summary():
    """DealAgent enriches note with LLM output when available."""
    provider = _make_provider()
    cluster = _make_cluster()

    canned = {"summary": "Great negotiated deal for students! Saving ₹200/mo."}
    fake_llm = FakeProvider(canned_response=canned, mode="valid")

    result = await run_deal_agent(provider, cluster, llm_provider=fake_llm)

    assert result.note == "Great negotiated deal for students! Saving ₹200/mo."
    assert fake_llm.call_count == 1
    # Numeric result is preserved
    assert result.floor <= result.final_price <= result.ceiling


@pytest.mark.asyncio
async def test_deal_agent_llm_failure_retains_template_note():
    """DealAgent catches LLM error and falls back to template string."""
    provider = _make_provider()
    cluster = _make_cluster()

    fake_llm = FakeProvider(mode="timeout")
    result = await run_deal_agent(provider, cluster, llm_provider=fake_llm)

    assert result.status in ("deal", "compromise")
    assert result.final_price is not None
    assert "reached" in result.note or "agreed" in result.note


# ---------------------------------------------------------------------------
# Hypothesis Property-Based Test (1,000+ examples)
# ---------------------------------------------------------------------------


@given(
    cost_per_meal=st.floats(min_value=15.0, max_value=60.0),
    min_margin=st.floats(min_value=0.05, max_value=0.30),
    list_price=st.floats(min_value=1500.0, max_value=4500.0),
    p_flexibility=st.floats(min_value=0.01, max_value=1.0),
    budget_ceiling=st.floats(min_value=1500.0, max_value=4500.0),
    headcount=st.integers(min_value=1, max_value=150),
    c_flexibility=st.floats(min_value=0.01, max_value=1.0),
    max_rounds=st.integers(min_value=1, max_value=10),
)
@settings(max_examples=1000, deadline=None)
def test_hypothesis_negotiation_invariant(
    cost_per_meal: float,
    min_margin: float,
    list_price: float,
    p_flexibility: float,
    budget_ceiling: float,
    headcount: int,
    c_flexibility: float,
    max_rounds: int,
):
    """Property test: whenever status != 'no_deal', floor <= final_price <= ceiling."""
    provider = _make_provider(
        cost_per_meal=cost_per_meal,
        min_margin=min_margin,
        list_price_monthly=list_price,
        flexibility=p_flexibility,
    )
    cluster = _make_cluster(
        budget_ceiling_monthly=budget_ceiling,
        headcount=headcount,
        flexibility=c_flexibility,
    )

    result = negotiate(provider, cluster, max_rounds=max_rounds)

    floor = round(cost_per_meal * 60.0 * (1.0 + min_margin), 2)
    ceiling = round(budget_ceiling, 2)

    if result.status == "no_deal":
        assert result.final_price is None
        assert floor > ceiling - 1e-4
        assert result.rounds == []
    else:
        assert result.status in ("deal", "compromise")
        assert result.final_price is not None
        # Strict invariant: floor <= final_price <= ceiling
        # Allow tiny 0.02 float rounding tolerance
        assert floor - 0.02 <= result.final_price <= ceiling + 0.02
        assert 1 <= len(result.rounds) <= max_rounds

        # Monotonicity check
        for i in range(len(result.rounds) - 1):
            assert result.rounds[i + 1].provider_ask <= result.rounds[i].provider_ask + 1e-4
            assert result.rounds[i + 1].cluster_bid >= result.rounds[i].cluster_bid - 1e-4
