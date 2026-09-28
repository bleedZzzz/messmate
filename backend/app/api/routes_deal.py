"""Route for Deal agent subscription price negotiation."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.deal import run_deal_agent
from app.api.deps import check_rate_limit, get_db, get_llm
from app.api.schemas import NegotiateRequest
from app.db import repositories
from app.llm.base import LLMProvider
from app.models.domain import NegotiationResult

router = APIRouter(tags=["deal"])


@router.post(
    "/negotiate",
    response_model=NegotiationResult,
    dependencies=[Depends(check_rate_limit)],
    summary="Simulate subscription negotiation",
    description="Invokes the Deal agent to simulate price negotiation.",
)
async def simulate_negotiation(
    payload: NegotiateRequest,
    db: Annotated[Session, Depends(get_db)],
    llm: Annotated[LLMProvider, Depends(get_llm)],
) -> NegotiationResult:
    """Run negotiation loop between student group and provider."""
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

    negotiation = await run_deal_agent(
        provider=provider,
        cluster=cluster,
        llm_provider=llm,
        max_rounds=payload.max_rounds,
    )
    return negotiation
