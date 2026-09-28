"""Routes for provider discovery and demand matching."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.demand import DemandRequest, run_demand_agent
from app.agents.match import run_match_agent
from app.agents.orchestrator import DbClusterSource
from app.api.deps import check_rate_limit, get_db
from app.api.schemas import MatchRequest, MatchResponse
from app.db.repositories import get_approved_providers

router = APIRouter(tags=["match"])


@router.post(
    "/match",
    response_model=MatchResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="Match providers to demand cluster",
    description="Selects the best demand cluster and ranks eligible providers.",
)
def match_providers(
    payload: MatchRequest,
    db: Annotated[Session, Depends(get_db)],
) -> MatchResponse:
    """Run Demand and Match agents to score providers against student clusters."""
    demand_req = DemandRequest(
        area=payload.area,
        lat=payload.lat,
        lon=payload.lon,
        radius_km=payload.radius_km,
        diet=payload.diet,
        budget_max=payload.budget_max,
        cluster_id=payload.cluster_id,
    )

    cluster_source = DbClusterSource(db)

    try:
        demand_res = run_demand_agent(demand_req, cluster_source)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    selected_cluster = demand_res.selected
    approved_providers = get_approved_providers(db)

    matches = run_match_agent(
        cluster=selected_cluster,
        providers=approved_providers,
        top_n=payload.top_n,
        radius_km=payload.radius_km,
    )

    return MatchResponse(cluster=selected_cluster, matches=matches)
