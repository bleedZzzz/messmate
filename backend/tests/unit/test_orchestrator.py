"""Unit tests for the LangGraph orchestrator (Milestone M5).

Covers:
- Happy path with FakeProvider (cluster, matches, menu, negotiation, 4 trace steps).
- No matches condition (early exit returning empty valid result, no errors).
- Partial failure handling (menu agent raises, negotiation still succeeds, error recorded).
- Pipeline execution with LLM_PROVIDER=none (NoneProvider fallback).
- Demand search failure handling.
"""

from unittest.mock import patch

import pytest

from app.agents.deal import NegotiationSummary
from app.agents.menu_fallback import generate_fallback_menu
from app.agents.orchestrator import (
    InMemoryClusterSource,
    InMemoryProviderSource,
    build_orchestrator_graph,
    run_pipeline,
)
from app.data.synthetic_generator import generate_clusters, generate_providers
from app.llm.base import FakeProvider, NoneProvider
from app.models.domain import MenuPlan, OptimizeRequest


@pytest.fixture(scope="module")
def sample_dataset():
    """Deterministic clusters and providers for testing."""
    providers = generate_providers(seed=42)
    clusters = generate_clusters(seed=42)
    return clusters, providers


@pytest.fixture
def sources(sample_dataset):
    clusters, providers = sample_dataset
    cluster_source = InMemoryClusterSource(clusters)
    provider_source = InMemoryProviderSource(providers)
    return cluster_source, provider_source


def _build_fake_llm(provider, cluster) -> FakeProvider:
    """Create a FakeProvider that provides valid MenuPlan and NegotiationSummary."""
    valid_menu = generate_fallback_menu(provider, cluster)
    valid_menu.source = "llm"
    valid_summary = NegotiationSummary(summary="Fair agreement reached with student group.")

    return FakeProvider(
        canned_responses={
            MenuPlan: valid_menu,
            NegotiationSummary: valid_summary,
        },
        mode="valid",
    )


@pytest.mark.asyncio
async def test_pipeline_happy_path_with_fake_provider(sample_dataset, sources):
    """Happy path with FakeProvider:
    returns cluster, matches, menu, negotiation, and 4 trace steps.
    """
    clusters, providers = sample_dataset
    cluster_source, provider_source = sources
    target_cluster = clusters[0]

    # Pre-determine winning provider to supply valid canned dishes for that catalog
    from app.agents.match import run_match_agent

    expected_matches = run_match_agent(target_cluster, providers, top_n=3, radius_km=10.0)
    top_provider_id = expected_matches[0].provider_id
    top_provider = next(p for p in providers if p.id == top_provider_id)

    fake_llm = _build_fake_llm(top_provider, target_cluster)

    request = OptimizeRequest(
        cluster_id=target_cluster.id,
        radius_km=10.0,
        top_n=3,
    )

    response = await run_pipeline(
        request,
        cluster_source=cluster_source,
        provider_source=provider_source,
        llm_provider=fake_llm,
    )

    # Output validations
    assert response.cluster is not None
    assert response.cluster.id == target_cluster.id
    assert len(response.matches) > 0
    assert response.top_provider is not None
    assert response.menu is not None
    assert response.menu.source == "llm"
    assert response.negotiation is not None
    assert response.negotiation.status in ("deal", "compromise")
    assert response.errors == []

    # Trace validations
    assert len(response.trace) == 4
    trace_agents = [step.agent for step in response.trace]
    assert trace_agents == ["demand", "match", "menu", "deal"]

    for step in response.trace:
        assert step.duration_ms >= 0
        assert step.error is None

    # LLM flags in trace
    demand_step = response.trace[0]
    assert demand_step.used_llm is False
    assert demand_step.fallback_used is False

    match_step = response.trace[1]
    assert match_step.used_llm is False
    assert match_step.fallback_used is False

    menu_step = response.trace[2]
    assert menu_step.used_llm is True
    assert menu_step.fallback_used is False

    deal_step = response.trace[3]
    assert deal_step.used_llm is True


@pytest.mark.asyncio
async def test_pipeline_no_matches_returns_empty_result_without_errors(sample_dataset, sources):
    """No matches returns an empty result without errors and stops before menu/deal."""
    clusters, _ = sample_dataset
    cluster_source, _ = sources
    target_cluster = clusters[0]

    # Empty provider source so no matches can be formed
    empty_provider_source = InMemoryProviderSource([])

    request = OptimizeRequest(
        cluster_id=target_cluster.id,
        radius_km=5.0,
    )

    response = await run_pipeline(
        request,
        cluster_source=cluster_source,
        provider_source=empty_provider_source,
        llm_provider=NoneProvider(),
    )

    assert response.cluster is not None
    assert response.cluster.id == target_cluster.id
    assert response.matches == []
    assert response.top_provider is None
    assert response.menu is None
    assert response.negotiation is None
    assert response.errors == []

    # Trace contains demand and match only
    assert len(response.trace) == 2
    assert [step.agent for step in response.trace] == ["demand", "match"]


@pytest.mark.asyncio
async def test_pipeline_partial_failure_menu_agent_raises(sample_dataset, sources):
    """If the menu agent raises, the response still contains the negotiation result
    and an error entry.
    """
    clusters, _ = sample_dataset
    cluster_source, provider_source = sources
    target_cluster = clusters[0]

    request = OptimizeRequest(
        cluster_id=target_cluster.id,
        radius_km=10.0,
    )

    with patch(
        "app.agents.orchestrator.run_menu_agent",
        side_effect=RuntimeError("Simulated LLM pipeline failure"),
    ):
        response = await run_pipeline(
            request,
            cluster_source=cluster_source,
            provider_source=provider_source,
            llm_provider=NoneProvider(),
        )

    # Menu failed, but negotiation still completed
    assert response.cluster is not None
    assert len(response.matches) > 0
    assert response.top_provider is not None
    assert response.menu is None
    assert response.negotiation is not None
    assert response.negotiation.status in ("deal", "compromise")

    # Errors recorded
    assert len(response.errors) == 1
    assert "menu: Simulated LLM pipeline failure" in response.errors[0]

    # Trace contains all 4 steps, with error on menu step
    assert len(response.trace) == 4
    menu_step = response.trace[2]
    assert menu_step.agent == "menu"
    assert menu_step.error is not None
    assert "Simulated LLM pipeline failure" in menu_step.error

    deal_step = response.trace[3]
    assert deal_step.agent == "deal"
    assert deal_step.error is None


@pytest.mark.asyncio
async def test_pipeline_works_with_none_provider(sample_dataset, sources):
    """The whole pipeline works with LLM_PROVIDER=none (NoneProvider fallback)."""
    clusters, _ = sample_dataset
    cluster_source, provider_source = sources
    target_cluster = clusters[0]

    request = OptimizeRequest(
        cluster_id=target_cluster.id,
        radius_km=10.0,
    )

    response = await run_pipeline(
        request,
        cluster_source=cluster_source,
        provider_source=provider_source,
        llm_provider=NoneProvider(),
    )

    assert response.cluster is not None
    assert len(response.matches) > 0
    assert response.top_provider is not None
    assert response.menu is not None
    assert response.menu.source == "fallback"
    assert response.negotiation is not None
    assert response.errors == []

    # Trace shows fallback was used for menu
    assert len(response.trace) == 4
    menu_step = response.trace[2]
    assert menu_step.used_llm is False
    assert menu_step.fallback_used is True


@pytest.mark.asyncio
async def test_pipeline_demand_failure_handled_gracefully(sources):
    """When demand agent finds no cluster, orchestrator returns error and empty result."""
    _, provider_source = sources

    # Empty cluster source will cause DemandAgent to raise ValueError
    empty_cluster_source = InMemoryClusterSource([])

    request = OptimizeRequest(area="NonExistentTown")

    response = await run_pipeline(
        request,
        cluster_source=empty_cluster_source,
        provider_source=provider_source,
        llm_provider=NoneProvider(),
    )

    assert response.cluster is None
    assert response.matches == []
    assert response.top_provider is None
    assert response.menu is None
    assert response.negotiation is None
    assert len(response.errors) >= 1
    assert "demand:" in response.errors[0]


@pytest.mark.asyncio
async def test_build_orchestrator_graph_structure():
    """Verify graph compiles properly with StateGraph."""
    graph = build_orchestrator_graph()
    assert graph is not None
