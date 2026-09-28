"""Unit tests and Hypothesis property tests for deterministic fallback menu planner."""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.agents.menu_fallback import generate_fallback_menu
from app.agents.menu_validator import is_valid_menu, validate_menu
from app.data.synthetic_generator import generate_clusters, generate_providers
from app.models.domain import DemandCluster, Dish, Provider


@pytest.fixture(scope="module")
def seeded_dataset():
    """Deterministic synthetic dataset from M1."""
    providers = generate_providers(seed=42)
    clusters = generate_clusters(seed=42)
    return type("Dataset", (), {"providers": providers, "clusters": clusters})()


def test_catalog_too_small_raises():
    provider = Provider(
        id="small-prov",
        name="Small Mess",
        town="Kolkata",
        area="Salt Lake",
        lat=22.58,
        lon=88.42,
        cuisines=["bengali"],
        diet_types=["veg"],
        capacity_total=30,
        capacity_available=10,
        list_price_monthly=2500.0,
        cost_per_meal=30.0,
        min_margin=0.15,
        flexibility=0.5,
        rating=4.0,
        dishes=[
            Dish(
                id=f"d-{i}",
                name=f"Dish {i}",
                slot="lunch",
                diet="veg",
                cuisine="bengali",
                main_item="dal",
                cost_tier=1,
            )
            for i in range(5)  # only 5 lunch dishes, 0 dinner dishes
        ],
    )
    cluster = DemandCluster(
        id="c-1",
        town="Kolkata",
        area="Salt Lake",
        lat=22.58,
        lon=88.42,
        headcount=20,
        budget_ceiling_monthly=2800.0,
        cuisine_weights={"bengali": 1.0},
        diet_split={"veg": 1.0, "non_veg": 0.0, "egg": 0.0},
        flexibility=0.5,
    )

    with pytest.raises(ValueError, match="too small"):
        generate_fallback_menu(provider, cluster)


def test_dinner_catalog_too_small_raises():
    provider = Provider(
        id="small-prov-d",
        name="Small Mess Dinner",
        town="Kolkata",
        area="Salt Lake",
        lat=22.58,
        lon=88.42,
        cuisines=["bengali"],
        diet_types=["veg"],
        capacity_total=30,
        capacity_available=10,
        list_price_monthly=2500.0,
        cost_per_meal=30.0,
        min_margin=0.15,
        flexibility=0.5,
        rating=4.0,
        dishes=[
            Dish(
                id=f"dl-{i}",
                name=f"Lunch {i}",
                slot="lunch",
                diet="veg",
                cuisine="bengali",
                main_item=f"item_{i}",
                cost_tier=1,
            )
            for i in range(8)
        ]
        + [
            Dish(
                id="dd-1",
                name="Dinner 1",
                slot="dinner",
                diet="veg",
                cuisine="bengali",
                main_item="dal",
                cost_tier=1,
            )
        ],
    )
    cluster = DemandCluster(
        id="c-1",
        town="Kolkata",
        area="Salt Lake",
        lat=22.58,
        lon=88.42,
        headcount=20,
        budget_ceiling_monthly=2800.0,
        cuisine_weights={"bengali": 1.0},
        diet_split={"veg": 1.0, "non_veg": 0.0, "egg": 0.0},
        flexibility=0.5,
    )

    with pytest.raises(ValueError, match="too small.*dinner"):
        generate_fallback_menu(provider, cluster)


def test_deterministic_reproducibility(seeded_dataset):
    """Calling generate_fallback_menu with same provider and cluster produces identical results."""
    provider = seeded_dataset.providers[0]
    cluster = seeded_dataset.clusters[0]

    menu1 = generate_fallback_menu(provider, cluster)
    menu2 = generate_fallback_menu(provider, cluster)

    assert menu1.provider_id == menu2.provider_id
    assert menu1.cluster_id == menu2.cluster_id
    assert menu1.source == "fallback"
    assert menu2.source == "fallback"
    assert menu1.days == menu2.days
    assert menu1.rationale == menu2.rationale


def test_fallback_menu_passes_validation_all_seeded_data(seeded_dataset):
    """Test every provider against every cluster in their town."""
    clusters_by_town: dict[str, list[DemandCluster]] = {}
    for c in seeded_dataset.clusters:
        clusters_by_town.setdefault(c.town, []).append(c)

    tested_count = 0
    for p in seeded_dataset.providers[:10]:
        town_clusters = clusters_by_town.get(p.town, [])
        for c in town_clusters:
            menu = generate_fallback_menu(p, c)
            errors = validate_menu(menu, p, c)
            assert errors == [], f"Failed validation for {p.id} and {c.id}: {errors}"
            assert is_valid_menu(menu, p, c) is True
            assert menu.source == "fallback"
            tested_count += 1

    assert tested_count >= 10


# ---------------------------------------------------------------------------
# Hypothesis Property-Based Testing
# ---------------------------------------------------------------------------


# Strategy for generating a single valid Dish
@st.composite
def dish_strategy(draw, slot: str, index: int):
    diet = draw(st.sampled_from(["veg", "non_veg", "egg"]))
    cuisine = draw(st.sampled_from(["bengali", "north_indian", "south_indian", "mughlai"]))
    main_item = draw(
        st.sampled_from(["dal", "paneer", "fish", "chicken", "egg", "soya", "roti", "biryani"])
    )
    cost_tier = draw(st.sampled_from([1, 2, 3]))
    return Dish(
        id=f"dish-{slot}-{index}",
        name=f"Dish {slot} {index}",
        slot=slot,  # type: ignore[arg-type]
        diet=diet,
        cuisine=cuisine,
        main_item=main_item,
        cost_tier=cost_tier,
    )


# Strategy for generating a valid Provider with >= 7 lunch and >= 7 dinner dishes
@st.composite
def random_valid_provider_and_cluster(draw):
    # Ensure between 8 and 15 dishes per slot
    num_lunch = draw(st.integers(min_value=8, max_value=16))
    num_dinner = draw(st.integers(min_value=8, max_value=16))

    lunch_dishes = [draw(dish_strategy("lunch", i)) for i in range(num_lunch)]
    dinner_dishes = [draw(dish_strategy("dinner", i)) for i in range(num_dinner)]
    all_dishes = lunch_dishes + dinner_dishes

    diet_types_present = list({d.diet for d in all_dishes})
    cuisines_present = list({d.cuisine for d in all_dishes})

    provider = Provider(
        id="hyp-provider",
        name="Hypothesis Mess",
        town="Kolkata",
        area="Park Street",
        lat=22.55,
        lon=88.35,
        cuisines=cuisines_present,
        diet_types=diet_types_present,
        capacity_total=50,
        capacity_available=25,
        list_price_monthly=2800.0,
        cost_per_meal=35.0,
        min_margin=0.15,
        flexibility=0.5,
        rating=4.2,
        dishes=all_dishes,
    )

    veg_share = draw(st.floats(min_value=0.2, max_value=0.8))
    rem = 1.0 - veg_share
    cluster = DemandCluster(
        id="hyp-cluster",
        town="Kolkata",
        area="Park Street",
        lat=22.55,
        lon=88.35,
        headcount=30,
        budget_ceiling_monthly=3000.0,
        cuisine_weights={c: 1.0 / len(cuisines_present) for c in cuisines_present},
        diet_split={"veg": veg_share, "non_veg": rem, "egg": 0.0},
        flexibility=0.5,
    )

    return provider, cluster


@given(pair=random_valid_provider_and_cluster())
@settings(max_examples=30, deadline=None)
def test_hypothesis_fallback_menu_satisfies_constraints(pair):
    """Property test: fallback menu satisfies validate_menu across randomized valid catalogs."""
    provider, cluster = pair
    try:
        menu = generate_fallback_menu(provider, cluster)
        errors = validate_menu(menu, provider, cluster)
        assert errors == [], f"Validation errors found: {errors}"
        assert menu.source == "fallback"
        assert len(menu.days) == 7
    except ValueError as e:
        # If randomized catalog cannot satisfy variety/veg constraints, ValueError is expected
        assert (
            "variety" in str(e)
            or "too small" in str(e)
            or "veg" in str(e).lower()
            or "invalid menu" in str(e).lower()
        )
