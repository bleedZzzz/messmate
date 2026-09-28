"""Menu validation logic enforcing ARCHITECTURE.md §6.3 domain constraints.

Constraints checked by validate_menu():
1. Exactly 7 days, each with valid lunch and dinner picks.
2. Every dish_id exists in the provider's catalog and matches the designated meal slot.
3. No dish repeats within the same slot across the 7 days (7 unique lunches, 7 unique dinners).
4. Veg share across the 14 weekly meals is within 10 percentage points of the cluster's
   veg split (when the provider offers non-veg options).
5. No main_item appears more than 3 times in the same meal slot across the 7 days.
"""

from __future__ import annotations

from collections import Counter

from app.models.domain import DemandCluster, Dish, MenuPlan, Provider


class MenuValidationError(ValueError):
    """Raised when a MenuPlan violates one or more business constraints."""


def validate_menu(
    menu: MenuPlan,
    provider: Provider,
    cluster: DemandCluster,
    *,
    raise_error: bool = False,
) -> list[str]:
    """Validate a menu plan against all section 6.3 domain rules.

    Args:
        menu: The MenuPlan to validate.
        provider: The provider offering the dishes.
        cluster: The demand cluster the menu is tailored for.
        raise_error: If True, raise MenuValidationError on first failure instead of collecting.

    Returns:
        A list of human-readable error descriptions. Empty if valid.
    """
    errors: list[str] = []

    # 1. Exactly 7 days
    if len(menu.days) != 7:
        errors.append(f"Menu must have exactly 7 days; found {len(menu.days)}.")

    days_seen: set[int] = set()
    for d in menu.days:
        if d.day < 1 or d.day > 7:
            errors.append(f"Invalid day number {d.day}; must be 1..7.")
        if d.day in days_seen:
            errors.append(f"Duplicate day number {d.day} in menu.")
        days_seen.add(d.day)

    # 2. Dish catalog lookup & slot matching
    catalog: dict[str, Dish] = {d.id: d for d in provider.dishes}

    lunch_ids: list[str] = []
    dinner_ids: list[str] = []

    for d in menu.days:
        # Check lunch pick
        if not d.lunch or not d.lunch.dish_id:
            errors.append(f"Day {d.day}: missing lunch pick.")
        elif d.lunch.dish_id not in catalog:
            errors.append(
                f"Day {d.day}: lunch dish_id '{d.lunch.dish_id}' not in provider catalog."
            )
        else:
            dish = catalog[d.lunch.dish_id]
            if dish.slot != "lunch":
                errors.append(
                    f"Day {d.day}: lunch dish '{dish.name}' has slot '{dish.slot}', "
                    "expected 'lunch'."
                )
            lunch_ids.append(d.lunch.dish_id)

        # Check dinner pick
        if not d.dinner or not d.dinner.dish_id:
            errors.append(f"Day {d.day}: missing dinner pick.")
        elif d.dinner.dish_id not in catalog:
            errors.append(
                f"Day {d.day}: dinner dish_id '{d.dinner.dish_id}' not in provider catalog."
            )
        else:
            dish = catalog[d.dinner.dish_id]
            if dish.slot != "dinner":
                errors.append(
                    f"Day {d.day}: dinner dish '{dish.name}' has slot '{dish.slot}', "
                    "expected 'dinner'."
                )
            dinner_ids.append(d.dinner.dish_id)

    # 3. No dish repeats within the same slot across the 7 days
    if len(lunch_ids) == 7 and len(set(lunch_ids)) != 7:
        lunch_dupes = [k for k, v in Counter(lunch_ids).items() if v > 1]
        errors.append(f"Lunch slot contains duplicate dishes across the week: {lunch_dupes}.")

    if len(dinner_ids) == 7 and len(set(dinner_ids)) != 7:
        dinner_dupes = [k for k, v in Counter(dinner_ids).items() if v > 1]
        errors.append(f"Dinner slot contains duplicate dishes across the week: {dinner_dupes}.")

    # 4. Veg share across the week within 10 percentage points of cluster split
    # Only applies when the provider offers non-veg (pure veg providers cannot produce non-veg)
    provider_offers_non_veg = any(d.diet != "veg" for d in provider.dishes)
    if provider_offers_non_veg and len(lunch_ids) == 7 and len(dinner_ids) == 7:
        lunch_non_veg = sum(1 for d in provider.dishes if d.slot == "lunch" and d.diet != "veg")
        dinner_non_veg = sum(1 for d in provider.dishes if d.slot == "dinner" and d.diet != "veg")
        min_possible_veg = max(0, 14 - (min(7, lunch_non_veg) + min(7, dinner_non_veg)))

        lunch_veg = sum(1 for d in provider.dishes if d.slot == "lunch" and d.diet == "veg")
        dinner_veg = sum(1 for d in provider.dishes if d.slot == "dinner" and d.diet == "veg")
        max_possible_veg = min(14, min(7, lunch_veg) + min(7, dinner_veg))

        cluster_veg_split = cluster.diet_split.get("veg", 0.0)
        achievable_target = max(
            min_possible_veg / 14.0,
            min(max_possible_veg / 14.0, cluster_veg_split),
        )

        total_meals = 14
        veg_meal_count = sum(1 for did in lunch_ids if catalog[did].diet == "veg") + sum(
            1 for did in dinner_ids if catalog[did].diet == "veg"
        )
        actual_veg_share = veg_meal_count / total_meals
        diff = abs(actual_veg_share - achievable_target)
        # 10 percentage points tolerance (0.10 + small float epsilon)
        if diff > 0.10 + 1e-5:
            errors.append(
                f"Weekly veg share {actual_veg_share:.1%} differs from cluster target "
                f"{achievable_target:.1%} by {diff:.1%} (allowed max: 10.0%)."
            )

    # 5. No main_item appears more than 3 times in the same slot
    if len(lunch_ids) == 7:
        lunch_main_counts = Counter(catalog[did].main_item for did in lunch_ids)
        for main_item, count in lunch_main_counts.items():
            if count > 3:
                errors.append(
                    f"Lunch slot has main_item '{main_item}' repeated {count} times (max 3)."
                )

    if len(dinner_ids) == 7:
        dinner_main_counts = Counter(catalog[did].main_item for did in dinner_ids)
        for main_item, count in dinner_main_counts.items():
            if count > 3:
                errors.append(
                    f"Dinner slot has main_item '{main_item}' repeated {count} times (max 3)."
                )

    if raise_error and errors:
        raise MenuValidationError("; ".join(errors))

    return errors


def is_valid_menu(menu: MenuPlan, provider: Provider, cluster: DemandCluster) -> bool:
    """Return True if the menu passes all validation constraints."""
    return len(validate_menu(menu, provider, cluster)) == 0
