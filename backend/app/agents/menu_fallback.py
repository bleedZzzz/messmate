"""Deterministic fallback menu planner for Tiffin Optimizer.

ARCHITECTURE.md §6.3:
- Fully deterministic, seeded by provider.id and cluster.id.
- Produces a 7-day rotating menu (lunch and dinner) passing validate_menu().
- Prioritizes dishes matching cluster cuisine weights.
- Enforces:
    - 7 unique lunch dishes and 7 unique dinner dishes
    - At most 3 repeats per main_item per slot
    - Veg share within 10 percentage points of cluster target (when non-veg is offered)
    - 2-sentence rationale without health/medical claims
"""

from __future__ import annotations

import hashlib
import math
from collections import Counter

from app.agents.menu_validator import validate_menu
from app.models.domain import DayMenu, DemandCluster, Dish, MealPick, MenuPlan, Provider


def _find_best_slot_combo(
    dishes: list[Dish],
    min_veg: int,
    max_veg: int,
    seed_str: str,
    cuisine_weights: dict[str, float],
) -> list[Dish] | None:
    """Find the best 7-dish combination satisfying main_item and veg constraints via DFS.

    Dishes are sorted by cuisine weight (descending) and deterministic hash.
    DFS finds the optimal set almost instantly because the search order is prioritized.
    """

    # Sort candidate dishes by priority: cuisine weight descending, then deterministic seed hash
    def dish_key(d: Dish) -> tuple[float, int]:
        c_weight = cuisine_weights.get(d.cuisine, 0.0)
        h = int(hashlib.sha256(f"{seed_str}:{d.id}".encode()).hexdigest()[:8], 16)
        return (c_weight, h)

    sorted_dishes = sorted(dishes, key=dish_key, reverse=True)
    n = len(sorted_dishes)

    main_counts: Counter[str] = Counter()
    selected: list[Dish] = []

    def dfs(idx: int, cur_veg: int) -> list[Dish] | None:
        if len(selected) == 7:
            if min_veg <= cur_veg <= max_veg:
                return list(selected)
            return None

        remaining_needed = 7 - len(selected)
        if n - idx < remaining_needed:
            return None

        # Prune if impossible to reach min_veg or stay under max_veg
        max_possible_veg = cur_veg + (n - idx)
        if max_possible_veg < min_veg:
            return None
        if cur_veg > max_veg:
            return None

        for i in range(idx, n):
            dish = sorted_dishes[i]
            if main_counts[dish.main_item] >= 3:
                continue

            is_veg = 1 if dish.diet == "veg" else 0
            if cur_veg + is_veg > max_veg:
                continue
            if cur_veg + is_veg + (6 - len(selected)) < min_veg:
                # Even if all remaining picks were veg, can't reach min_veg
                continue

            main_counts[dish.main_item] += 1
            selected.append(dish)

            result = dfs(i + 1, cur_veg + is_veg)
            if result is not None:
                return result

            selected.pop()
            main_counts[dish.main_item] -= 1

        return None

    return dfs(0, 0)


def generate_fallback_menu(provider: Provider, cluster: DemandCluster) -> MenuPlan:
    """Generate a fully deterministic 7-day MenuPlan passing all domain constraints.

    Args:
        provider: Provider offering the dishes.
        cluster: Target demand cluster.

    Returns:
        Validated MenuPlan with source='fallback'.

    Raises:
        ValueError: If provider catalog has fewer than 7 lunch/dinner dishes or lacks variety.
    """
    lunch_catalog = [d for d in provider.dishes if d.slot == "lunch"]
    dinner_catalog = [d for d in provider.dishes if d.slot == "dinner"]

    if len(lunch_catalog) < 7:
        raise ValueError(
            f"Provider catalog too small for 7-day rotation: "
            f"has {len(lunch_catalog)} lunch dishes (minimum 7 required)."
        )
    if len(dinner_catalog) < 7:
        raise ValueError(
            f"Provider catalog too small for 7-day rotation: "
            f"has {len(dinner_catalog)} dinner dishes (minimum 7 required)."
        )

    provider_offers_non_veg = any(d.diet != "veg" for d in provider.dishes)
    cluster_veg_ratio = cluster.diet_split.get("veg", 0.0)

    # Determine achievable bounds based on catalog
    lunch_non_veg = sum(1 for d in lunch_catalog if d.diet != "veg")
    dinner_non_veg = sum(1 for d in dinner_catalog if d.diet != "veg")
    min_possible_veg = max(0, 14 - (min(7, lunch_non_veg) + min(7, dinner_non_veg)))

    lunch_veg = sum(1 for d in lunch_catalog if d.diet == "veg")
    dinner_veg = sum(1 for d in dinner_catalog if d.diet == "veg")
    max_possible_veg = min(14, min(7, lunch_veg) + min(7, dinner_veg))

    achievable_veg_ratio = max(
        min_possible_veg / 14.0,
        min(max_possible_veg / 14.0, cluster_veg_ratio),
    )

    if provider_offers_non_veg:
        min_total_veg = max(min_possible_veg, math.ceil(14 * (achievable_veg_ratio - 0.10 - 1e-6)))
        max_total_veg = min(max_possible_veg, math.floor(14 * (achievable_veg_ratio + 0.10 + 1e-6)))
        target_total_veg = round(achievable_veg_ratio * 14)
        target_total_veg = max(min_total_veg, min(max_total_veg, target_total_veg))
    else:
        min_total_veg = min_possible_veg
        max_total_veg = max_possible_veg
        target_total_veg = max_possible_veg

    seed_str = f"{provider.id}:{cluster.id}"

    # Target slot split
    ideal_lunch_veg = max(0, min(7, target_total_veg // 2))
    ideal_dinner_veg = target_total_veg - ideal_lunch_veg

    # Search candidate lunch and dinner picks
    lunch_picks: list[Dish] | None = None
    dinner_picks: list[Dish] | None = None

    lunch_targets = sorted(range(8), key=lambda v: abs(v - ideal_lunch_veg))
    for l_veg in lunch_targets:
        candidate_lunch = _find_best_slot_combo(
            lunch_catalog,
            min_veg=l_veg,
            max_veg=l_veg,
            seed_str=f"{seed_str}:lunch:{l_veg}",
            cuisine_weights=cluster.cuisine_weights,
        )
        if candidate_lunch is None:
            continue

        l_actual_veg = sum(1 for d in candidate_lunch if d.diet == "veg")
        d_min = max(0, min_total_veg - l_actual_veg)
        d_max = min(7, max_total_veg - l_actual_veg)
        if d_min > d_max:
            continue

        dinner_targets = sorted(range(d_min, d_max + 1), key=lambda v: abs(v - ideal_dinner_veg))
        for d_veg in dinner_targets:
            candidate_dinner = _find_best_slot_combo(
                dinner_catalog,
                min_veg=d_veg,
                max_veg=d_veg,
                seed_str=f"{seed_str}:dinner:{d_veg}",
                cuisine_weights=cluster.cuisine_weights,
            )
            if candidate_dinner is not None:
                lunch_picks = candidate_lunch
                dinner_picks = candidate_dinner
                break
        if lunch_picks is not None:
            break

    # If strict range failed, find any valid lunch and dinner that minimize veg deviation
    if lunch_picks is None or dinner_picks is None:
        best_diff = 999
        for l_v in lunch_targets:
            candidate_lunch = _find_best_slot_combo(
                lunch_catalog,
                min_veg=l_v,
                max_veg=l_v,
                seed_str=f"{seed_str}:lunch:{l_v}",
                cuisine_weights=cluster.cuisine_weights,
            )
            if candidate_lunch is None:
                continue
            for d_v in range(8):
                candidate_dinner = _find_best_slot_combo(
                    dinner_catalog,
                    min_veg=d_v,
                    max_veg=d_v,
                    seed_str=f"{seed_str}:dinner:{d_v}",
                    cuisine_weights=cluster.cuisine_weights,
                )
                if candidate_dinner is not None:
                    diff = abs((l_v + d_v) - target_total_veg)
                    if diff < best_diff:
                        best_diff = diff
                        lunch_picks = candidate_lunch
                        dinner_picks = candidate_dinner
                        if diff == 0:
                            break
            if lunch_picks is not None and best_diff <= 1:
                break

    if lunch_picks is None or dinner_picks is None:
        raise ValueError(
            "Provider catalog lacks variety: unable to select 7 dishes where "
            "no main item repeats > 3 times."
        )

    # Build DayMenu items
    days: list[DayMenu] = []
    for i in range(7):
        days.append(
            DayMenu(
                day=i + 1,
                lunch=MealPick(dish_id=lunch_picks[i].id, name=lunch_picks[i].name),
                dinner=MealPick(dish_id=dinner_picks[i].id, name=dinner_picks[i].name),
            )
        )

    # Build concise 2-sentence rationale with zero health/medical claims
    top_cuisines = [
        c for c, _ in sorted(cluster.cuisine_weights.items(), key=lambda kv: kv[1], reverse=True)
    ]
    cuisine_pref = top_cuisines[0].title() if top_cuisines else "Local"

    rationale = (
        f"Weekly 7-day rotating menu tailored to {cluster.town} ({cluster.area}) preferences. "
        f"Features {cuisine_pref} specialties with daily protein and vegetable rotation "
        "across lunch and dinner."
    )

    plan = MenuPlan(
        provider_id=provider.id,
        cluster_id=cluster.id,
        days=days,
        rationale=rationale,
        source="fallback",
    )

    # Validate output to guarantee compliance
    errors = validate_menu(plan, provider, cluster)
    if errors:
        raise ValueError(f"Fallback menu generation produced invalid menu: {'; '.join(errors)}")

    return plan
