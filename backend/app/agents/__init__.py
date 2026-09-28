"""Agents package for Tiffin Optimizer."""

from app.agents.deal import DealAgent, compute_volume_discount, negotiate, run_deal_agent
from app.agents.demand import ClusterSource, DemandRequest, DemandResult, run_demand_agent
from app.agents.geo import haversine_km
from app.agents.match import run_match_agent
from app.agents.menu import build_menu_prompt, run_menu_agent
from app.agents.menu_fallback import generate_fallback_menu
from app.agents.menu_validator import MenuValidationError, is_valid_menu, validate_menu
from app.agents.orchestrator import (
    DbClusterSource,
    DbProviderSource,
    InMemoryClusterSource,
    InMemoryProviderSource,
    PipelineState,
    ProviderSource,
    build_orchestrator_graph,
    run_pipeline,
    run_step,
)

__all__ = [
    "ClusterSource",
    "DbClusterSource",
    "DbProviderSource",
    "DealAgent",
    "DemandRequest",
    "DemandResult",
    "InMemoryClusterSource",
    "InMemoryProviderSource",
    "MenuValidationError",
    "PipelineState",
    "ProviderSource",
    "build_menu_prompt",
    "build_orchestrator_graph",
    "compute_volume_discount",
    "generate_fallback_menu",
    "haversine_km",
    "is_valid_menu",
    "negotiate",
    "run_deal_agent",
    "run_demand_agent",
    "run_match_agent",
    "run_menu_agent",
    "run_pipeline",
    "run_step",
    "validate_menu",
]
