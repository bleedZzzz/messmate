"""Agents package for Tiffin Optimizer."""

from app.agents.demand import ClusterSource, DemandRequest, DemandResult, run_demand_agent
from app.agents.geo import haversine_km
from app.agents.match import run_match_agent
from app.agents.menu import build_menu_prompt, run_menu_agent
from app.agents.menu_fallback import generate_fallback_menu
from app.agents.menu_validator import MenuValidationError, is_valid_menu, validate_menu

__all__ = [
    "ClusterSource",
    "DemandRequest",
    "DemandResult",
    "MenuValidationError",
    "build_menu_prompt",
    "generate_fallback_menu",
    "haversine_km",
    "is_valid_menu",
    "run_demand_agent",
    "run_match_agent",
    "run_menu_agent",
    "validate_menu",
]
