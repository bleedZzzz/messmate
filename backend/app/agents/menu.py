"""Menu agent for Tiffin Optimizer (LLM with deterministic fallback).

ARCHITECTURE.md §6.3 & PRD FR-8 to FR-11:
- Input: Provider (with dish catalog), DemandCluster
- Output: MenuPlan
- Flow:
    1. Build prompt containing dish catalog, cluster diet split, cuisine weights, constraints.
    2. Call LLMProvider.generate_structured(prompt, MenuPlan) with timeout and up to 2 retries.
    3. Validate with validate_menu(). On any failure (timeout, schema, constraints), run fallback.
    4. Set source to "llm" or "fallback".
- Prompt rules:
    - Model may only pick from supplied dish IDs
    - Rationale limited to max 2 sentences
    - Strict prohibition on health/medical claims
"""

from __future__ import annotations

import logging

from app.agents.menu_fallback import generate_fallback_menu
from app.agents.menu_validator import validate_menu
from app.llm.base import LLMProvider, LLMUnavailable, NoneProvider
from app.models.domain import DemandCluster, MenuPlan, Provider

logger = logging.getLogger(__name__)


def build_menu_prompt(provider: Provider, cluster: DemandCluster) -> str:
    """Construct prompt for structured MenuPlan generation."""
    # List dishes with their id, name, slot, diet, cuisine, and main_item
    dish_lines = [
        f"  - ID: {d.id} | Name: {d.name} | Slot: {d.slot} | "
        f"Diet: {d.diet} | Cuisine: {d.cuisine} | Main: {d.main_item}"
        for d in provider.dishes
    ]
    catalog_text = "\n".join(dish_lines)

    cuisine_str = ", ".join(f"{c}: {w:.0%}" for c, w in cluster.cuisine_weights.items())
    diet_str = ", ".join(f"{d}: {s:.0%}" for d, s in cluster.diet_split.items())
    offers_non_veg = "Yes" if any(d.diet != "veg" for d in provider.dishes) else "No"
    veg_pref = f"{cluster.diet_split.get('veg', 0.0):.0%}"

    return (
        "You are the Menu Planning Agent for Tiffin Optimizer.\n"
        f"Generate a 7-day meal plan (lunch & dinner, days 1..7) for students in "
        f"{cluster.town} ({cluster.area}).\n\n"
        f"Cluster Preferences:\n"
        f"- Target Cuisines: {cuisine_str}\n"
        f"- Diet Distribution: {diet_str}\n\n"
        f"Provider Dish Catalog:\n"
        f"{catalog_text}\n\n"
        "Rules & Constraints:\n"
        "1. Days: Exactly 7 days (day: 1..7) with 'lunch' and 'dinner' MealPick (dish_id & name).\n"
        "2. Allowed Dishes: Pick ONLY from the supplied dish IDs above. Do NOT invent new IDs.\n"
        "3. Slot Matching: Lunch picks must have Slot='lunch'. Dinner picks Slot='dinner'.\n"
        "4. No Slot Repeats: No dish ID may appear more than once in lunch (7 unique lunches) "
        "and dinner (7 unique dinners).\n"
        f"5. Veg Balance: Provider offers non-veg? {offers_non_veg}. Veg meal percentage across "
        f"all 14 meals must be within 10 percentage points of cluster target ({veg_pref}).\n"
        "6. Main Item Variety: No single 'Main' item (e.g. fish, dal, paneer) > 3 times per slot.\n"
        "7. Rationale: At most 2 sentences explaining rotation.\n"
        "8. Compliance: Do NOT make any medical or health claims.\n"
    )


async def run_menu_agent(
    provider: Provider,
    cluster: DemandCluster,
    llm_provider: LLMProvider | None = None,
    *,
    timeout: float = 20.0,
    max_retries: int = 2,
) -> MenuPlan:
    """Run Menu agent with structured LLM generation and automatic deterministic fallback.

    Args:
        provider: Provider with full dish catalog.
        cluster: Target demand cluster.
        llm_provider: Implementation of LLMProvider protocol (defaults to NoneProvider).
        timeout: Per-attempt timeout in seconds.
        max_retries: Number of retries on LLM/validation failure (total attempts = 1 + max_retries).

    Returns:
        Validated MenuPlan marked with source='llm' or source='fallback'.
    """
    effective_provider = llm_provider if llm_provider is not None else NoneProvider()
    total_attempts = 1 + max(0, max_retries)

    if not isinstance(effective_provider, NoneProvider):
        prompt = build_menu_prompt(provider, cluster)

        for attempt in range(1, total_attempts + 1):
            try:
                candidate: MenuPlan = await effective_provider.generate_structured(
                    prompt=prompt,
                    schema=MenuPlan,
                    timeout=timeout,
                )

                # Ensure IDs match input
                candidate.provider_id = provider.id
                candidate.cluster_id = cluster.id

                # Validate domain constraints
                errors = validate_menu(candidate, provider, cluster)
                if not errors:
                    # Valid LLM generation succeeded!
                    candidate.source = "llm"
                    return candidate

                logger.warning(
                    "LLM menu attempt %d/%d failed validation: %s",
                    attempt,
                    total_attempts,
                    "; ".join(errors),
                )

            except (TimeoutError, LLMUnavailable, Exception) as exc:
                logger.warning(
                    "LLM menu attempt %d/%d encountered error: %s",
                    attempt,
                    total_attempts,
                    exc,
                )

    # Fallback path if LLM is disabled, timed out, invalid, or exhausted retries
    return generate_fallback_menu(provider, cluster)
