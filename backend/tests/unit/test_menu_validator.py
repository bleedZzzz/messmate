"""Unit tests for menu validation logic enforcing ARCHITECTURE.md §6.3 rules."""

import pytest

from app.agents.menu_validator import MenuValidationError, is_valid_menu, validate_menu
from app.models.domain import DayMenu, DemandCluster, Dish, MealPick, MenuPlan, Provider


def _make_sample_provider() -> Provider:
    """Create a sample provider with 10 lunch dishes and 10 dinner dishes."""
    dishes: list[Dish] = []
    # 10 lunch dishes: 6 veg, 4 non_veg, 2 main items each max 3 times
    for i in range(1, 11):
        slot = "lunch"
        diet = "veg" if i <= 6 else "non_veg"
        main = "dal" if i <= 3 else "paneer" if i <= 6 else "fish" if i <= 8 else "chicken"
        dishes.append(
            Dish(
                id=f"p1-l-{i}",
                name=f"Lunch Dish {i}",
                slot=slot,
                diet=diet,
                cuisine="bengali",
                main_item=main,
                cost_tier=1,
            )
        )
    # 10 dinner dishes: 6 veg, 4 non_veg
    for i in range(1, 11):
        slot = "dinner"
        diet = "veg" if i <= 6 else "non_veg"
        main = "roti_sabzi" if i <= 3 else "soya" if i <= 6 else "egg" if i <= 8 else "mutton"
        dishes.append(
            Dish(
                id=f"p1-d-{i}",
                name=f"Dinner Dish {i}",
                slot=slot,
                diet=diet,
                cuisine="bengali",
                main_item=main,
                cost_tier=1,
            )
        )

    return Provider(
        id="prov-1",
        name="Annapurna Mess",
        town="Kolkata",
        area="Jadavpur",
        lat=22.498,
        lon=88.371,
        cuisines=["bengali"],
        diet_types=["veg", "non_veg"],
        capacity_total=50,
        capacity_available=20,
        list_price_monthly=2800.0,
        cost_per_meal=35.0,
        min_margin=0.15,
        flexibility=0.5,
        rating=4.5,
        dishes=dishes,
    )


def _make_sample_cluster(veg_split: float = 0.50) -> DemandCluster:
    return DemandCluster(
        id="clust-1",
        town="Kolkata",
        area="Jadavpur",
        lat=22.499,
        lon=88.372,
        headcount=30,
        budget_ceiling_monthly=3000.0,
        cuisine_weights={"bengali": 1.0},
        diet_split={"veg": veg_split, "non_veg": 1.0 - veg_split, "egg": 0.0},
        flexibility=0.5,
    )


def _make_valid_menu(provider: Provider, cluster: DemandCluster) -> MenuPlan:
    days: list[DayMenu] = []
    # 7 lunch picks: 4 veg, 3 non-veg
    # 7 dinner picks: 3 veg, 4 non-veg
    # Total veg = 7/14 = 50%
    lunch_ids = ["p1-l-1", "p1-l-2", "p1-l-3", "p1-l-4", "p1-l-7", "p1-l-8", "p1-l-9"]
    dinner_ids = ["p1-d-1", "p1-d-2", "p1-d-3", "p1-d-7", "p1-d-8", "p1-d-9", "p1-d-10"]

    catalog = {d.id: d for d in provider.dishes}
    for day in range(1, 8):
        l_id = lunch_ids[day - 1]
        d_id = dinner_ids[day - 1]
        days.append(
            DayMenu(
                day=day,
                lunch=MealPick(dish_id=l_id, name=catalog[l_id].name),
                dinner=MealPick(dish_id=d_id, name=catalog[d_id].name),
            )
        )

    return MenuPlan(
        provider_id=provider.id,
        cluster_id=cluster.id,
        days=days,
        rationale="Balanced 7-day meal plan. Bengali homestyle rotation.",
        source="llm",
    )


def test_valid_menu_passes_validation():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster(veg_split=0.50)
    menu = _make_valid_menu(provider, cluster)

    errors = validate_menu(menu, provider, cluster)
    assert errors == []
    assert is_valid_menu(menu, provider, cluster) is True


def test_constraint_not_7_days():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    # 6 days
    menu.days = menu.days[:6]
    errors = validate_menu(menu, provider, cluster)
    assert any("exactly 7 days" in e for e in errors)
    assert is_valid_menu(menu, provider, cluster) is False


def test_constraint_invalid_day_numbers():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    # Duplicate day number
    menu.days[1].day = 1
    errors = validate_menu(menu, provider, cluster)
    assert any("Duplicate day number" in e for e in errors)

    # Day out of 1..7 range
    menu.days[1].day = 9
    errors2 = validate_menu(menu, provider, cluster)
    assert any("must be 1..7" in e for e in errors2)


def test_constraint_missing_picks():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    # Empty dish_id
    menu.days[0].lunch.dish_id = ""
    menu.days[0].dinner.dish_id = ""
    errors = validate_menu(menu, provider, cluster)
    assert any("missing lunch pick" in e for e in errors)
    assert any("missing dinner pick" in e for e in errors)


def test_constraint_unknown_dish_id():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    menu.days[0].lunch.dish_id = "non-existent-dish-id"
    menu.days[0].dinner.dish_id = "non-existent-dinner-id"
    errors = validate_menu(menu, provider, cluster)
    assert any("lunch dish_id 'non-existent-dish-id' not in provider catalog" in e for e in errors)
    assert any(
        "dinner dish_id 'non-existent-dinner-id' not in provider catalog" in e for e in errors
    )


def test_constraint_wrong_slot():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    # Put a dinner dish into lunch pick and lunch dish into dinner pick
    menu.days[0].lunch.dish_id = "p1-d-1"
    menu.days[0].dinner.dish_id = "p1-l-1"
    errors = validate_menu(menu, provider, cluster)
    assert any("expected 'lunch'" in e for e in errors)
    assert any("expected 'dinner'" in e for e in errors)


def test_constraint_duplicate_dish_in_same_slot():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    # Repeat Day 1 lunch on Day 2 and Day 1 dinner on Day 2
    menu.days[1].lunch.dish_id = menu.days[0].lunch.dish_id
    menu.days[1].dinner.dish_id = menu.days[0].dinner.dish_id
    errors = validate_menu(menu, provider, cluster)
    assert any("Lunch slot contains duplicate dishes" in e for e in errors)
    assert any("Dinner slot contains duplicate dishes" in e for e in errors)


def test_constraint_main_item_repeat_over_3():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    # Add a 4th "dal" dish to lunch catalog and menu
    new_dal = Dish(
        id="p1-l-dal4",
        name="Another Dal",
        slot="lunch",
        diet="veg",
        cuisine="bengali",
        main_item="dal",
        cost_tier=1,
    )
    provider.dishes.append(new_dal)
    # Replace Day 4 lunch (which was paneer) with this 4th dal
    menu.days[3].lunch.dish_id = "p1-l-dal4"

    errors = validate_menu(menu, provider, cluster)
    assert any("main_item 'dal' repeated 4 times" in e for e in errors)


def test_constraint_dinner_main_item_repeat_over_3():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)

    new_roti = Dish(
        id="p1-d-roti4",
        name="Another Roti",
        slot="dinner",
        diet="veg",
        cuisine="bengali",
        main_item="roti_sabzi",
        cost_tier=1,
    )
    provider.dishes.append(new_roti)
    menu.days[3].dinner.dish_id = "p1-d-roti4"

    errors = validate_menu(menu, provider, cluster)
    assert any("main_item 'roti_sabzi' repeated 4 times" in e for e in errors)


def test_constraint_veg_share_out_of_bounds():
    provider = _make_sample_provider()
    # Cluster wants 50% veg (target: 7 veg out of 14 meals, range allowed: 40% to 60%)
    cluster = _make_sample_cluster(veg_split=0.50)
    menu = _make_valid_menu(provider, cluster)

    # Change all dinners to non-veg (dishes 7, 8, 9, 10 are non_veg, add 3 more non_veg)
    for i in range(11, 14):
        provider.dishes.append(
            Dish(
                id=f"p1-d-{i}",
                name=f"Extra Non-Veg {i}",
                slot="dinner",
                diet="non_veg",
                cuisine="bengali",
                main_item=f"item_{i}",
                cost_tier=1,
            )
        )
    # Dinner now has 0 veg meals
    menu.days[0].dinner.dish_id = "p1-d-7"
    menu.days[1].dinner.dish_id = "p1-d-8"
    menu.days[2].dinner.dish_id = "p1-d-9"
    menu.days[3].dinner.dish_id = "p1-d-10"
    menu.days[4].dinner.dish_id = "p1-d-11"
    menu.days[5].dinner.dish_id = "p1-d-12"
    menu.days[6].dinner.dish_id = "p1-d-13"

    # Now total veg = 4 lunches out of 14 meals = 28.5%, which is < 40%
    errors = validate_menu(menu, provider, cluster)
    assert any("Weekly veg share" in e for e in errors)


def test_pure_veg_provider_skips_non_veg_constraint():
    """Pure veg providers cannot offer non-veg, so 100% veg is accepted."""
    provider = _make_sample_provider()
    # Remove all non-veg dishes
    provider.dishes = [d for d in provider.dishes if d.diet == "veg"]
    provider.diet_types = ["veg"]

    cluster = _make_sample_cluster(veg_split=0.40)  # cluster wanted 40% veg

    # Add a 7th veg dish
    provider.dishes.append(
        Dish(
            id="p1-l-veg7",
            name="Veg 7",
            slot="lunch",
            diet="veg",
            cuisine="bengali",
            main_item="item_v7",
            cost_tier=1,
        )
    )
    provider.dishes.append(
        Dish(
            id="p1-d-veg7",
            name="Veg 7 D",
            slot="dinner",
            diet="veg",
            cuisine="bengali",
            main_item="item_v7d",
            cost_tier=1,
        )
    )

    days: list[DayMenu] = []
    l_ids = [f"p1-l-{i}" for i in range(1, 7)] + ["p1-l-veg7"]
    d_ids = [f"p1-d-{i}" for i in range(1, 7)] + ["p1-d-veg7"]
    for day in range(1, 8):
        days.append(
            DayMenu(
                day=day,
                lunch=MealPick(dish_id=l_ids[day - 1], name="V"),
                dinner=MealPick(dish_id=d_ids[day - 1], name="V"),
            )
        )

    menu = MenuPlan(
        provider_id=provider.id,
        cluster_id=cluster.id,
        days=days,
        rationale="Pure veg rotation.",
        source="fallback",
    )

    errors = validate_menu(menu, provider, cluster)
    assert errors == []


def test_raise_error_flag():
    provider = _make_sample_provider()
    cluster = _make_sample_cluster()
    menu = _make_valid_menu(provider, cluster)
    menu.days = []  # invalid

    with pytest.raises(MenuValidationError, match="exactly 7 days"):
        validate_menu(menu, provider, cluster, raise_error=True)
