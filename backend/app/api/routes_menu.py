"""Route for Menu agent meal planning."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.menu import run_menu_agent
from app.api.deps import check_rate_limit, get_db, get_llm
from app.api.schemas import MenuRequest
from app.db import repositories
from app.llm.base import LLMProvider
from app.models.domain import MenuPlan

router = APIRouter(tags=["menu"])


@router.post(
    "/menu",
    response_model=MenuPlan,
    dependencies=[Depends(check_rate_limit)],
    summary="Generate 7-day meal plan",
    description="Invokes the Menu planning agent for a provider and cluster pair.",
)
async def generate_menu(
    payload: MenuRequest,
    db: Annotated[Session, Depends(get_db)],
    llm: Annotated[LLMProvider, Depends(get_llm)],
) -> MenuPlan:
    """Generate 7-day rotating menu plan with diet balancing."""
    provider = repositories.get_provider_by_id(db, payload.provider_id)
    if provider is None:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{payload.provider_id}' not found",
        )

    cluster = repositories.get_cluster_by_id(db, payload.cluster_id)
    if cluster is None:
        raise HTTPException(
            status_code=404,
            detail=f"Demand cluster '{payload.cluster_id}' not found",
        )

    menu_plan = await run_menu_agent(provider=provider, cluster=cluster, llm_provider=llm)
    return menu_plan
