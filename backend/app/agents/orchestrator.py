"""LangGraph orchestrator for the Tiffin Optimizer multi-agent pipeline.

ARCHITECTURE.md §6.5 & PRD FR-17, FR-18:
- Stateful execution of Demand, Match, Menu, and Deal agents.
- Conditional edge after Match: stops early with an empty but valid result if no matches.
- Wraps every agent in `run_step()` for timing, trace recording, and partial failure tolerance.
- Fully typed domain inputs (OptimizeRequest) and outputs (OptimizeResponse).
"""

from __future__ import annotations

import inspect
import logging
import time
from collections.abc import Callable
from typing import Any, Protocol, TypedDict, runtime_checkable

from langgraph.graph import END, StateGraph

from app.agents.deal import run_deal_agent
from app.agents.demand import ClusterSource, DemandRequest, DemandResult, run_demand_agent
from app.agents.match import run_match_agent
from app.agents.menu import run_menu_agent
from app.llm.base import LLMProvider, NoneProvider
from app.models.domain import (
    DemandCluster,
    MenuPlan,
    NegotiationResult,
    OptimizeRequest,
    OptimizeResponse,
    Provider,
    ProviderMatch,
    TraceStep,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# ProviderSource protocol and in-memory test doubles
# ---------------------------------------------------------------------------


@runtime_checkable
class ProviderSource(Protocol):
    """Pluggable data source for providers."""

    def get_all(self) -> list[Provider]:
        """Return every provider in the data source."""
        ...

    def get_by_id(self, provider_id: str) -> Provider | None:
        """Return a single provider by ID, or None."""
        ...


class InMemoryClusterSource:
    """In-memory ClusterSource for tests or offline usage."""

    def __init__(self, clusters: list[DemandCluster]) -> None:
        self._clusters = {c.id: c for c in clusters}

    def get_all(self) -> list[DemandCluster]:
        return list(self._clusters.values())

    def get_by_id(self, cluster_id: str) -> DemandCluster | None:
        return self._clusters.get(cluster_id)


class InMemoryProviderSource:
    """In-memory ProviderSource for tests or offline usage."""

    def __init__(self, providers: list[Provider]) -> None:
        self._providers = {p.id: p for p in providers}

    def get_all(self) -> list[Provider]:
        return list(self._providers.values())

    def get_by_id(self, provider_id: str) -> Provider | None:
        return self._providers.get(provider_id)


# ---------------------------------------------------------------------------
# PipelineState (ARCHITECTURE.md §6.5)
# ---------------------------------------------------------------------------


class PipelineState(TypedDict, total=False):
    """Shared state dictionary passed through the orchestrator graph."""

    request: OptimizeRequest
    clusters: list[DemandCluster]
    cluster: DemandCluster
    matches: list[ProviderMatch]
    provider: Provider
    menu: MenuPlan
    negotiation: NegotiationResult
    trace: list[TraceStep]
    errors: list[str]
    response: OptimizeResponse


# ---------------------------------------------------------------------------
# run_step wrapper (FR-18 & ARCHITECTURE.md §6.5)
# ---------------------------------------------------------------------------


async def run_step(
    state: PipelineState,
    agent_name: str,
    func: Callable[..., Any],
    *args: Any,
    used_llm: bool = False,
    fallback_used: bool = False,
    **kwargs: Any,
) -> Any:
    """Execute an agent step with observability and partial failure tolerance.

    Records a TraceStep (agent, started_ms, duration_ms, used_llm, fallback_used, error),
    catches all exceptions, appends error message to state['errors'], and allows the
    pipeline to continue safely.
    """
    start_time = time.time()
    started_ms = int(start_time * 1000)
    error_msg: str | None = None
    result: Any = None
    actual_used_llm = used_llm
    actual_fallback_used = fallback_used

    try:
        if inspect.iscoroutinefunction(func):
            result = await func(*args, **kwargs)
        else:
            res = func(*args, **kwargs)
            if inspect.isawaitable(res):
                result = await res
            else:
                result = res

        # Derive LLM / fallback flags from result when available
        if isinstance(result, MenuPlan):
            if result.source == "llm":
                actual_used_llm = True
                actual_fallback_used = False
            else:
                actual_used_llm = False
                actual_fallback_used = True

    except Exception as exc:
        error_msg = f"{agent_name}: {exc}"
        logger.warning("Agent step '%s' failed: %s", agent_name, exc)
        if "errors" not in state or state["errors"] is None:
            state["errors"] = []
        state["errors"].append(error_msg)

    duration_ms = max(0, int((time.time() - start_time) * 1000))
    step = TraceStep(
        agent=agent_name,
        started_ms=started_ms,
        duration_ms=duration_ms,
        used_llm=actual_used_llm,
        fallback_used=actual_fallback_used,
        error=error_msg,
    )

    if "trace" not in state or state["trace"] is None:
        state["trace"] = []
    state["trace"].append(step)

    return result


# ---------------------------------------------------------------------------
# Graph node builders
# ---------------------------------------------------------------------------


def create_demand_node(
    cluster_source: ClusterSource | None = None,
) -> Callable[[PipelineState], Any]:
    """Factory for the 'demand' agent node."""

    async def demand_node(state: PipelineState) -> dict[str, Any]:
        req = state.get("request") or OptimizeRequest()
        source = cluster_source or InMemoryClusterSource([])

        demand_req = DemandRequest(
            area=req.area,
            lat=req.lat,
            lon=req.lon,
            radius_km=req.radius_km,
            diet=req.diet,
            budget_max=req.budget_max,
            cluster_id=req.cluster_id or req.area_id,
        )

        demand_res: DemandResult | None = await run_step(
            state,
            "demand",
            run_demand_agent,
            demand_req,
            source,
            used_llm=False,
            fallback_used=False,
        )

        updates: dict[str, Any] = {
            "trace": list(state.get("trace", [])),
            "errors": list(state.get("errors", [])),
        }
        if demand_res is not None:
            updates["clusters"] = demand_res.clusters
            updates["cluster"] = demand_res.selected
        return updates

    return demand_node


def create_match_node(
    provider_source: ProviderSource | None = None,
) -> Callable[[PipelineState], Any]:
    """Factory for the 'match' agent node."""

    async def match_node(state: PipelineState) -> dict[str, Any]:
        cluster = state.get("cluster")
        req = state.get("request") or OptimizeRequest()

        if cluster is None:
            empty_resp = OptimizeResponse(
                cluster=None,
                matches=[],
                top_provider=None,
                menu=None,
                negotiation=None,
                trace=list(state.get("trace", [])),
                errors=list(state.get("errors", [])),
            )
            return {
                "matches": [],
                "provider": None,
                "response": empty_resp,
                "trace": list(state.get("trace", [])),
                "errors": list(state.get("errors", [])),
            }

        source = provider_source or InMemoryProviderSource([])
        all_providers = source.get_all()

        matches: list[ProviderMatch] | None = await run_step(
            state,
            "match",
            run_match_agent,
            cluster,
            all_providers,
            req.top_n,
            req.radius_km,
            used_llm=False,
            fallback_used=False,
        )

        matches_list = matches or []
        top_provider: Provider | None = None
        if matches_list:
            top_id = matches_list[0].provider_id
            top_provider = source.get_by_id(top_id)
            if top_provider is None:
                top_provider = next((p for p in all_providers if p.id == top_id), None)

        updates: dict[str, Any] = {
            "matches": matches_list,
            "provider": top_provider,
            "trace": list(state.get("trace", [])),
            "errors": list(state.get("errors", [])),
        }

        # Early exit preparation if no matches found
        if not matches_list or top_provider is None:
            updates["response"] = OptimizeResponse(
                cluster=cluster,
                matches=[],
                top_provider=None,
                menu=None,
                negotiation=None,
                trace=list(state.get("trace", [])),
                errors=list(state.get("errors", [])),
            )

        return updates

    return match_node


def has_matches(state: PipelineState) -> str:
    """Conditional edge condition: checks if any provider match exists."""
    matches = state.get("matches")
    provider = state.get("provider")
    if matches and len(matches) > 0 and provider is not None:
        return "yes"
    return "no"


def create_menu_node(
    llm_provider: LLMProvider | None = None,
) -> Callable[[PipelineState], Any]:
    """Factory for the 'menu' agent node."""

    async def menu_node(state: PipelineState) -> dict[str, Any]:
        cluster = state.get("cluster")
        provider = state.get("provider")

        if cluster is None or provider is None:
            return {
                "trace": list(state.get("trace", [])),
                "errors": list(state.get("errors", [])),
            }

        effective_llm = llm_provider or NoneProvider()
        used_llm_flag = not isinstance(effective_llm, NoneProvider)

        menu_plan: MenuPlan | None = await run_step(
            state,
            "menu",
            run_menu_agent,
            provider,
            cluster,
            effective_llm,
            used_llm=used_llm_flag,
        )

        updates: dict[str, Any] = {
            "trace": list(state.get("trace", [])),
            "errors": list(state.get("errors", [])),
        }
        if menu_plan is not None:
            updates["menu"] = menu_plan
        return updates

    return menu_node


def create_deal_node(
    llm_provider: LLMProvider | None = None,
) -> Callable[[PipelineState], Any]:
    """Factory for the 'deal' agent node."""

    async def deal_node(state: PipelineState) -> dict[str, Any]:
        cluster = state.get("cluster")
        provider = state.get("provider")

        if cluster is None or provider is None:
            return {
                "trace": list(state.get("trace", [])),
                "errors": list(state.get("errors", [])),
            }

        effective_llm = llm_provider or NoneProvider()
        used_llm_flag = not isinstance(effective_llm, NoneProvider)

        negotiation: NegotiationResult | None = await run_step(
            state,
            "deal",
            run_deal_agent,
            provider,
            cluster,
            effective_llm,
            used_llm=used_llm_flag,
            fallback_used=False,
        )

        updates: dict[str, Any] = {
            "trace": list(state.get("trace", [])),
            "errors": list(state.get("errors", [])),
        }
        if negotiation is not None:
            updates["negotiation"] = negotiation
        return updates

    return deal_node


def assemble_node(state: PipelineState) -> dict[str, Any]:
    """Assemble final OptimizeResponse from pipeline state."""
    response = OptimizeResponse(
        cluster=state.get("cluster"),
        matches=state.get("matches", []),
        top_provider=state.get("provider"),
        menu=state.get("menu"),
        negotiation=state.get("negotiation"),
        trace=list(state.get("trace", [])),
        errors=list(state.get("errors", [])),
    )
    return {
        "response": response,
        "trace": list(state.get("trace", [])),
        "errors": list(state.get("errors", [])),
    }


# ---------------------------------------------------------------------------
# Graph compilation & pipeline execution
# ---------------------------------------------------------------------------


def build_orchestrator_graph(
    cluster_source: ClusterSource | None = None,
    provider_source: ProviderSource | None = None,
    llm_provider: LLMProvider | None = None,
) -> Any:
    """Build and compile the LangGraph StateGraph pipeline."""
    graph: Any = StateGraph(PipelineState)

    graph.add_node("demand", create_demand_node(cluster_source))
    graph.add_node("match", create_match_node(provider_source))
    graph.add_node("menu", create_menu_node(llm_provider))
    graph.add_node("deal", create_deal_node(llm_provider))
    graph.add_node("assemble", assemble_node)

    graph.set_entry_point("demand")
    graph.add_edge("demand", "match")
    graph.add_conditional_edges("match", has_matches, {"yes": "menu", "no": END})
    graph.add_edge("menu", "deal")
    graph.add_edge("deal", "assemble")
    graph.add_edge("assemble", END)

    return graph.compile()


async def run_pipeline(
    request: OptimizeRequest,
    *,
    cluster_source: ClusterSource | None = None,
    provider_source: ProviderSource | None = None,
    llm_provider: LLMProvider | None = None,
) -> OptimizeResponse:
    """Run full optimization pipeline and return an OptimizeResponse."""
    app = build_orchestrator_graph(
        cluster_source=cluster_source,
        provider_source=provider_source,
        llm_provider=llm_provider,
    )

    initial_state: PipelineState = {
        "request": request,
        "trace": [],
        "errors": [],
    }

    final_state = await app.ainvoke(initial_state)

    response: OptimizeResponse | None = final_state.get("response")
    if response is None:
        response = OptimizeResponse(
            cluster=final_state.get("cluster"),
            matches=final_state.get("matches", []),
            top_provider=final_state.get("provider"),
            menu=final_state.get("menu"),
            negotiation=final_state.get("negotiation"),
            trace=list(final_state.get("trace", [])),
            errors=list(final_state.get("errors", [])),
        )

    return response
