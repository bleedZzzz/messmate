"""Synthetic data generator for Tiffin Optimizer.

Generates reproducible (seeded) synthetic providers, dishes, and demand clusters
for 8+ West Bengal towns.  All phone numbers use the obviously-fake +91 00000 0XXXX
format so they can never be mistaken for real numbers.
"""

import json
import random
import string
from pathlib import Path
from typing import Any, cast

from app.models.domain import DemandCluster, Dish, Provider

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TOWNS_PATH = Path(__file__).parent / "towns.json"

_CUISINES = ["bengali", "north_indian", "south_indian", "chinese"]

_PROVIDER_NAME_PREFIXES = [
    "Maa",
    "Annapurna",
    "Bharat",
    "Durga",
    "Sagar",
    "Sandhya",
    "Sarada",
    "Bhojan",
    "Nirmala",
    "Shanti",
    "Swagat",
    "Bikash",
    "Rupali",
    "Suruchi",
    "Basundhara",
    "Aaheli",
    "Trishna",
    "Subarna",
    "Prabhat",
    "Kolkata",
]

_PROVIDER_NAME_SUFFIXES = [
    "Tiffin Service",
    "Mess",
    "Kitchen",
    "Bhojanalaya",
    "Caterers",
    "Home Food",
    "Tiffin Centre",
    "Food Hub",
    "Rasoi",
    "Bhandar",
]

# Dish catalog — each entry: (name, slot, diet, cuisine, main_item, cost_tier)
_DISH_CATALOG: list[tuple[str, str, str, str, str, int]] = [
    # Bengali lunch — veg
    ("Aloo Posto", "lunch", "veg", "bengali", "vegetables", 1),
    ("Begun Bhaja", "lunch", "veg", "bengali", "vegetables", 1),
    ("Moong Dal", "lunch", "veg", "bengali", "dal", 1),
    ("Cholar Dal", "lunch", "veg", "bengali", "dal", 2),
    ("Shukto", "lunch", "veg", "bengali", "vegetables", 2),
    ("Labra", "lunch", "veg", "bengali", "vegetables", 1),
    ("Paneer Dalna", "lunch", "veg", "bengali", "paneer", 2),
    ("Kumro Bhaja", "lunch", "veg", "bengali", "vegetables", 1),
    ("Aloo Bhaja", "lunch", "veg", "bengali", "vegetables", 1),
    ("Posto Bora", "lunch", "veg", "bengali", "vegetables", 1),
    ("Dhokar Dalna", "lunch", "veg", "bengali", "dal", 2),
    ("Chholar Dal Niramish", "lunch", "veg", "bengali", "dal", 1),
    # Bengali lunch — non-veg / egg
    ("Macher Jhol", "lunch", "non_veg", "bengali", "fish", 2),
    ("Doi Maach", "lunch", "non_veg", "bengali", "fish", 3),
    ("Chingri Malai Curry", "lunch", "non_veg", "bengali", "fish", 3),
    ("Chicken Curry Bengali", "lunch", "non_veg", "bengali", "chicken", 2),
    ("Kosha Mangsho", "lunch", "non_veg", "bengali", "mutton", 3),
    ("Dim Curry", "lunch", "egg", "bengali", "egg", 1),
    ("Dim Bhaja", "lunch", "egg", "bengali", "egg", 1),
    # Bengali dinner
    ("Luchi Alur Dom", "dinner", "veg", "bengali", "vegetables", 2),
    ("Khichuri", "dinner", "veg", "bengali", "dal", 1),
    ("Ghee Bhat Dal", "dinner", "veg", "bengali", "dal", 1),
    ("Veg Pulao Bengali", "dinner", "veg", "bengali", "vegetables", 2),
    ("Chicken Biryani Bengali", "dinner", "non_veg", "bengali", "chicken", 3),
    ("Fish Fry Rice", "dinner", "non_veg", "bengali", "fish", 3),
    ("Mutton Biryani Bengali", "dinner", "non_veg", "bengali", "mutton", 3),
    ("Egg Biryani Bengali", "dinner", "egg", "bengali", "egg", 2),
    ("Roti Sabzi Bengali", "dinner", "veg", "bengali", "vegetables", 1),
    ("Aloo Paratha", "dinner", "veg", "bengali", "vegetables", 1),
    # North Indian lunch — veg
    ("Dal Tadka", "lunch", "veg", "north_indian", "dal", 1),
    ("Rajma Chawal", "lunch", "veg", "north_indian", "dal", 1),
    ("Paneer Butter Masala", "lunch", "veg", "north_indian", "paneer", 2),
    ("Kadhai Paneer", "lunch", "veg", "north_indian", "paneer", 2),
    ("Shahi Paneer", "lunch", "veg", "north_indian", "paneer", 3),
    ("Aloo Gobi", "lunch", "veg", "north_indian", "vegetables", 1),
    ("Chole Bhature", "lunch", "veg", "north_indian", "dal", 2),
    ("Mix Veg Curry", "lunch", "veg", "north_indian", "vegetables", 1),
    ("Palak Paneer", "lunch", "veg", "north_indian", "paneer", 2),
    ("Baingan Bharta", "lunch", "veg", "north_indian", "vegetables", 1),
    # North Indian lunch — non-veg / egg
    ("Butter Chicken", "lunch", "non_veg", "north_indian", "chicken", 3),
    ("Chicken Curry NI", "lunch", "non_veg", "north_indian", "chicken", 2),
    ("Egg Bhurji", "lunch", "egg", "north_indian", "egg", 1),
    ("Mutton Rogan Josh", "lunch", "non_veg", "north_indian", "mutton", 3),
    # North Indian dinner
    ("Roti Dal Fry", "dinner", "veg", "north_indian", "dal", 1),
    ("Dal Makhani", "dinner", "veg", "north_indian", "dal", 2),
    ("Paneer Tikka Wrap", "dinner", "veg", "north_indian", "paneer", 2),
    ("Veg Biryani NI", "dinner", "veg", "north_indian", "vegetables", 2),
    ("Chicken Biryani NI", "dinner", "non_veg", "north_indian", "chicken", 3),
    ("Egg Roll NI", "dinner", "egg", "north_indian", "egg", 1),
    ("Chicken Tikka Plate", "dinner", "non_veg", "north_indian", "chicken", 2),
    ("Mutton Biryani NI", "dinner", "non_veg", "north_indian", "mutton", 3),
    # South Indian lunch
    ("Sambar Rice", "lunch", "veg", "south_indian", "dal", 1),
    ("Masala Dosa", "lunch", "veg", "south_indian", "vegetables", 1),
    ("Lemon Rice", "lunch", "veg", "south_indian", "vegetables", 1),
    ("Curd Rice", "lunch", "veg", "south_indian", "dal", 1),
    ("Chicken Chettinad", "lunch", "non_veg", "south_indian", "chicken", 3),
    # South Indian dinner
    ("Idli Sambar", "dinner", "veg", "south_indian", "dal", 1),
    ("Uttapam", "dinner", "veg", "south_indian", "vegetables", 1),
    ("Appam Stew Veg", "dinner", "veg", "south_indian", "vegetables", 2),
    ("Appam Egg Curry", "dinner", "egg", "south_indian", "egg", 2),
    # Chinese
    ("Veg Fried Rice", "lunch", "veg", "chinese", "vegetables", 1),
    ("Chicken Fried Rice", "lunch", "non_veg", "chinese", "chicken", 2),
    ("Egg Chowmein", "lunch", "egg", "chinese", "egg", 1),
    ("Paneer Chilli", "lunch", "veg", "chinese", "paneer", 2),
    ("Veg Noodles", "dinner", "veg", "chinese", "vegetables", 1),
    ("Chicken Chowmein", "dinner", "non_veg", "chinese", "chicken", 2),
    ("Egg Fried Rice", "dinner", "egg", "chinese", "egg", 1),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_towns() -> list[dict[str, Any]]:
    with open(_TOWNS_PATH, encoding="utf-8") as f:
        result: list[dict[str, Any]] = json.load(f)
        return result


def _fake_phone(rng: random.Random) -> str:
    """Return a phone number in the obviously-fake +91 00000 0XXXX format."""
    last_four = "".join(rng.choices(string.digits, k=4))
    return f"+91 00000 0{last_four}"


def _make_slug(text: str) -> str:
    """Convert 'College Para' → 'college-para'."""
    return text.lower().replace(" ", "-")


def _pick_cuisines(rng: random.Random, town_name: str) -> list[str]:
    """Pick 1–3 cuisines, Bengali-heavy for Bengal towns."""
    weights = {"bengali": 0.55, "north_indian": 0.25, "south_indian": 0.10, "chinese": 0.10}
    if town_name in ("Siliguri",):
        weights = {"bengali": 0.30, "north_indian": 0.40, "south_indian": 0.10, "chinese": 0.20}

    n = rng.choices([1, 2, 3], weights=[0.3, 0.5, 0.2])[0]
    selected: list[str] = []
    pool = list(weights.keys())
    w = [weights[c] for c in pool]
    while len(selected) < n and pool:
        pick = rng.choices(pool, weights=w, k=1)[0]
        if pick not in selected:
            selected.append(pick)
        idx = pool.index(pick)
        pool.pop(idx)
        w.pop(idx)
    return selected if selected else ["bengali"]


def _make_dishes(
    rng: random.Random,
    provider_id: str,
    cuisines: list[str],
    diet_types: list[str],
) -> list[Dish]:
    """Pick 25–40 dishes from the catalog matching provider cuisines and diets."""
    eligible = [d for d in _DISH_CATALOG if d[3] in cuisines and d[2] in diet_types]
    if len(eligible) < 25:
        # supplement with all-cuisine dishes to hit minimum
        eligible = [d for d in _DISH_CATALOG if d[2] in diet_types]

    target = rng.randint(25, min(40, len(eligible)))
    picked = rng.sample(eligible, min(target, len(eligible)))

    # Ensure at least one dish per slot
    slots_present = {d[1] for d in picked}
    for needed_slot in ("lunch", "dinner"):
        if needed_slot not in slots_present:
            candidates = [d for d in _DISH_CATALOG if d[1] == needed_slot and d[2] in diet_types]
            if candidates:
                picked.append(rng.choice(candidates))

    dishes: list[Dish] = []
    for i, (name, slot, diet, cuisine, main_item, cost_tier) in enumerate(picked):
        dishes.append(
            Dish(
                id=f"{provider_id}-dish-{i:03d}",
                name=name,
                slot=slot,  # type: ignore[arg-type]
                diet=diet,  # type: ignore[arg-type]
                cuisine=cuisine,
                main_item=main_item,
                cost_tier=cost_tier,  # type: ignore[arg-type]
            )
        )
    return dishes


def _normalize_weights(d: dict[str, float]) -> dict[str, float]:
    """Normalize values so they sum to 1.0."""
    total = sum(d.values())
    if total == 0:
        n = len(d)
        return {k: 1.0 / n for k in d}
    return {k: round(v / total, 4) for k, v in d.items()}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate_providers(seed: int = 42) -> list[Provider]:
    """Generate synthetic providers for all towns. Deterministic for a given seed."""
    rng = random.Random(seed)
    towns = _load_towns()
    providers: list[Provider] = []

    for town in towns:
        n_providers = rng.randint(8, 20)
        areas = town["areas"]

        for i in range(n_providers):
            area = rng.choice(areas)
            town_slug = _make_slug(town["name"])
            area_slug = _make_slug(area["name"])
            pid = f"{town_slug}-{area_slug}-p{i:03d}"

            cuisines = _pick_cuisines(rng, town["name"])
            # determine diet types offered
            diet_pool: list[str] = ["veg"]
            if rng.random() < 0.70:
                diet_pool.append("non_veg")
            if rng.random() < 0.60:
                diet_pool.append("egg")

            capacity_total = rng.randint(15, 120)
            capacity_available = rng.randint(0, capacity_total)
            list_price = round(rng.uniform(2200, 3800), 0)
            cost_per_meal = round(list_price / 60 * rng.uniform(0.55, 0.75), 2)

            prefix = rng.choice(_PROVIDER_NAME_PREFIXES)
            suffix = rng.choice(_PROVIDER_NAME_SUFFIXES)
            name = f"{prefix} {suffix}"

            dishes = _make_dishes(rng, pid, cuisines, diet_pool)

            # small jitter around the area coordinates
            lat = area["lat"] + rng.uniform(-0.005, 0.005)
            lon = area["lon"] + rng.uniform(-0.005, 0.005)

            providers.append(
                Provider(
                    id=pid,
                    name=name,
                    town=town["name"],
                    area=area["name"],
                    lat=round(lat, 6),
                    lon=round(lon, 6),
                    cuisines=cuisines,
                    diet_types=diet_pool,  # type: ignore[arg-type]
                    capacity_total=capacity_total,
                    capacity_available=capacity_available,
                    list_price_monthly=list_price,
                    cost_per_meal=cost_per_meal,
                    min_margin=round(rng.uniform(0.10, 0.25), 2),
                    flexibility=round(rng.uniform(0.10, 0.60), 2),
                    rating=round(rng.uniform(2.5, 5.0), 1),
                    dishes=dishes,
                    phone=_fake_phone(rng),
                    status="approved",
                )
            )

    return providers


def generate_clusters(seed: int = 42) -> list[DemandCluster]:
    """Generate synthetic demand clusters for all towns. Deterministic for a given seed."""
    rng = random.Random(seed)
    towns = _load_towns()
    clusters: list[DemandCluster] = []

    for town in towns:
        n_clusters = rng.randint(2, 4)
        # pick areas that are college or hostel type preferentially
        college_areas = [a for a in town["areas"] if a.get("type") in ("college", "hostel")]
        pool = college_areas if college_areas else town["areas"]

        for i in range(n_clusters):
            area = pool[i % len(pool)]
            town_slug = _make_slug(town["name"])
            area_slug = _make_slug(area["name"])
            cid = f"{town_slug}-{area_slug}-c{i:03d}"

            # cuisine weights: bengali-heavy for Bengal
            raw_weights: dict[str, float] = {}
            for c in _CUISINES:
                if c == "bengali":
                    raw_weights[c] = rng.uniform(0.35, 0.60)
                elif c == "north_indian":
                    raw_weights[c] = rng.uniform(0.15, 0.35)
                else:
                    raw_weights[c] = rng.uniform(0.02, 0.15)
            cuisine_weights = _normalize_weights(raw_weights)

            # diet split
            veg_share = rng.uniform(0.30, 0.60)
            nonveg_share = rng.uniform(0.20, 0.50)
            egg_share = 1.0 - veg_share - nonveg_share
            if egg_share < 0:
                # re-balance
                nonveg_share = 1.0 - veg_share - 0.05
                egg_share = 0.05
            raw_diet: dict[str, float] = {
                "veg": veg_share,
                "non_veg": nonveg_share,
                "egg": egg_share,
            }
            diet_split = _normalize_weights(raw_diet)

            lat = area["lat"] + rng.uniform(-0.003, 0.003)
            lon = area["lon"] + rng.uniform(-0.003, 0.003)

            clusters.append(
                DemandCluster(
                    id=cid,
                    town=town["name"],
                    area=area["name"],
                    lat=round(lat, 6),
                    lon=round(lon, 6),
                    headcount=rng.randint(8, 80),
                    budget_ceiling_monthly=round(rng.uniform(2000, 3500), 0),
                    cuisine_weights=cuisine_weights,
                    diet_split=cast(dict, diet_split),
                    flexibility=round(rng.uniform(0.10, 0.60), 2),
                )
            )

    return clusters


def validate_phone_is_fake(phone: str) -> bool:
    """Return True if the phone matches the obviously-fake +91 00000 0XXXX pattern."""
    if not phone.startswith("+91 00000 0"):
        return False
    suffix = phone.replace("+91 00000 0", "")
    return len(suffix) == 4 and suffix.isdigit()
