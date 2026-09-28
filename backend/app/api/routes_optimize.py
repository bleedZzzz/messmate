"""Route for full LangGraph pipeline optimization."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.orchestrator import DbClusterSource, DbProviderSource, run_pipeline
from app.api.deps import check_rate_limit, get_db, get_llm
from app.llm.base import LLMProvider
from app.models.domain import OptimizeRequest, OptimizeResponse

router = APIRouter(tags=["optimize"])


@router.post(
    "/optimize",
    response_model=OptimizeResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="Run full optimization pipeline",
    description="Orchestrates Demand, Match, Menu, and Deal agents via LangGraph.",
)
async def optimize_pipeline(
    payload: OptimizeRequest,
    db: Annotated[Session, Depends(get_db)],
    llm: Annotated[LLMProvider, Depends(get_llm)],
) -> OptimizeResponse:
    """Execute complete multi-agent workflow and return unified response."""
    cluster_source = DbClusterSource(db)
    provider_source = DbProviderSource(db)

    response = await run_pipeline(
        request=payload,
        cluster_source=cluster_source,
        provider_source=provider_source,
        llm_provider=llm,
    )
    return response
