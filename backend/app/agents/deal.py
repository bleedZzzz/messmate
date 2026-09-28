"""Deal agent — simulates monthly subscription price negotiation.

ARCHITECTURE.md §6.4 & PRD FR-12 to FR-16:
- Pure deterministic negotiation loop between provider and cluster.
- Computes:
    floor    = provider.cost_per_meal * 60 * (1 + provider.min_margin)
    ceiling  = cluster.budget_ceiling_monthly
    discount = 0.00 if headcount < 10 else 0.05 if headcount < 25 else 0.10
    ask      = max(floor, provider.list_price_monthly * (1 - discount))
    bid      = ceiling * 0.80
- Statuses:
    - no_deal: if floor > ceiling
    - deal: if bid >= ask within max_rounds
    - compromise: if max_rounds reached, price = clamp((ask + bid)/2, floor, ceiling)
- Invariant: whenever status != "no_deal", floor <= final_price <= ceiling.
- Monotonicity: ask never increases, bid never decreases.
- Optional LLM summary with deterministic template fallback.
"""

from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel

from app.llm.base import LLMProvider, LLMUnavailable, NoneProvider
from app.models.domain import DemandCluster, NegotiationResult, NegotiationRound, Provider

logger = logging.getLogger(__name__)


class NegotiationSummary(BaseModel):
    """Structured LLM output schema for negotiation summary."""

    summary: str


def compute_volume_discount(headcount: int) -> float:
    """Return volume discount fraction based on cluster headcount."""
    if headcount < 10:
        return 0.00
    if headcount < 25:
        return 0.05
    return 0.10


def _build_template_note(
    status: Literal["deal", "compromise", "no_deal"],
    final_price: float | None,
    floor: float,
    ceiling: float,
    discount: float,
    round_count: int,
) -> str:
    """Deterministic fallback summary text."""
    if status == "no_deal":
        return (
            f"Unable to reach agreement: provider minimum cost (₹{floor:.0f}/mo) "
            f"exceeds group budget ceiling (₹{ceiling:.0f}/mo). "
            "Consider fewer meals per week or opting for a cheaper plan tier."
        )
    if status == "deal":
        return (
            f"Deal agreed in round {round_count} at ₹{final_price:.0f}/month per member "
            f"with a {discount:.0%} volume discount applied. Both parties reached consensus."
        )
    # compromise
    return (
        f"Compromise reached after {round_count} rounds at suggested ₹{final_price:.0f}/month "
        f"per member ({discount:.0%} group discount). Balances mess margin with student budget."
    )


def negotiate(
    provider: Provider,
    cluster: DemandCluster,
    max_rounds: int = 5,
) -> NegotiationResult:
    """Execute deterministic price negotiation simulation (pure function).

    Args:
        provider: Provider offering tiffin services.
        cluster: Demand cluster with headcount and budget ceiling.
        max_rounds: Maximum negotiation rounds (default: 5).

    Returns:
        NegotiationResult containing status, rounds timeline, and final price.
    """
    # 1. Setup
    floor = provider.cost_per_meal * 60.0 * (1.0 + provider.min_margin)
    ceiling = float(cluster.budget_ceiling_monthly)
    discount = compute_volume_discount(cluster.headcount)

    # 2. Check infeasible deal
    if floor > ceiling:
        note = _build_template_note("no_deal", None, floor, ceiling, discount, 0)
        return NegotiationResult(
            status="no_deal",
            final_price=None,
            floor=round(floor, 2),
            ceiling=round(ceiling, 2),
            volume_discount=discount,
            rounds=[],
            note=note,
        )

    ask = max(floor, provider.list_price_monthly * (1.0 - discount))
    bid = ceiling * 0.80

    rounds: list[NegotiationRound] = []
    status: Literal["deal", "compromise", "no_deal"] = "compromise"
    final_price: float | None = None

    # 3. Negotiation loop
    for r in range(1, max_rounds + 1):
        rounds.append(
            NegotiationRound(
                round=r,
                provider_ask=round(ask, 2),
                cluster_bid=round(bid, 2),
            )
        )

        if bid >= ask:
            status = "deal"
            final_price = (ask + bid) / 2.0
            break

        # Concessions for next round
        ask = ask - provider.flexibility * (ask - floor)
        bid = bid + cluster.flexibility * (ceiling - bid)

    # 4. If loop exhausted without deal -> compromise
    if status == "compromise":
        raw_price = (ask + bid) / 2.0
        # Clamp strictly between floor and ceiling
        final_price = max(floor, min(ceiling, raw_price))

    final_price_rounded = round(final_price, 2) if final_price is not None else None
    note = _build_template_note(status, final_price_rounded, floor, ceiling, discount, len(rounds))

    return NegotiationResult(
        status=status,
        final_price=final_price_rounded,
        floor=round(floor, 2),
        ceiling=round(ceiling, 2),
        volume_discount=discount,
        rounds=rounds,
        note=note,
    )


class DealAgent:
    """Thin wrapper class for Deal agent with optional LLM summary."""

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        self.llm_provider = llm_provider or NoneProvider()

    def negotiate(
        self,
        provider: Provider,
        cluster: DemandCluster,
        max_rounds: int = 5,
    ) -> NegotiationResult:
        """Run pure synchronous negotiation."""
        return negotiate(provider, cluster, max_rounds=max_rounds)

    async def run(
        self,
        provider: Provider,
        cluster: DemandCluster,
        max_rounds: int = 5,
    ) -> NegotiationResult:
        """Run negotiation and optionally enrich note with LLM summary."""
        result = self.negotiate(provider, cluster, max_rounds=max_rounds)

        if not isinstance(self.llm_provider, NoneProvider):
            try:
                prompt = (
                    "Summarize this tiffin subscription price negotiation in at most "
                    "2 friendly sentences.\n"
                    f"Provider: {provider.name} in {provider.town}\n"
                    f"Cluster: {cluster.town} ({cluster.area}), {cluster.headcount} members\n"
                    f"Outcome: {result.status}\n"
                    f"Final Price: ₹{result.final_price or 'N/A'}/month "
                    f"(Floor: ₹{result.floor}, Ceiling: ₹{result.ceiling})\n"
                    f"Rounds: {len(result.rounds)}\n"
                    "Do not invent new numbers. Keep it encouraging and under 2 sentences."
                )
                summary_data: NegotiationSummary = await self.llm_provider.generate_structured(
                    prompt, NegotiationSummary, timeout=5.0
                )
                if summary_data.summary.strip():
                    result.note = summary_data.summary.strip()
            except (LLMUnavailable, TimeoutError, Exception) as exc:
                logger.debug("Deal LLM summary failed, retaining template note: %s", exc)

        return result


async def run_deal_agent(
    provider: Provider,
    cluster: DemandCluster,
    llm_provider: LLMProvider | None = None,
    max_rounds: int = 5,
) -> NegotiationResult:
    """Convenience function to run Deal agent."""
    agent = DealAgent(llm_provider=llm_provider)
    return await agent.run(provider, cluster, max_rounds=max_rounds)
