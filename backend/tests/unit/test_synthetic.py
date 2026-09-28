"""Tests for the synthetic data generator."""

import math
import re

from app.data.synthetic_generator import (
    generate_clusters,
    generate_providers,
    validate_phone_is_fake,
)


class TestDeterminism:
    """Generation must be reproducible for a fixed seed."""

    def test_providers_deterministic(self) -> None:
        p1 = generate_providers(seed=42)
        p2 = generate_providers(seed=42)
        assert len(p1) == len(p2)
        for a, b in zip(p1, p2, strict=True):
            assert a.id == b.id
            assert a.name == b.name
            assert a.lat == b.lat

    def test_clusters_deterministic(self) -> None:
        c1 = generate_clusters(seed=42)
        c2 = generate_clusters(seed=42)
        assert len(c1) == len(c2)
        for a, b in zip(c1, c2, strict=True):
            assert a.id == b.id
            assert a.headcount == b.headcount

    def test_different_seeds_differ(self) -> None:
        p1 = generate_providers(seed=42)
        p2 = generate_providers(seed=99)
        # At minimum the coordinates and ratings will differ
        assert p1[0].rating != p2[0].rating or p1[0].lat != p2[0].lat


class TestProviderProperties:
    """Every generated provider must satisfy invariants."""

    def test_provider_count_per_town(self) -> None:
        providers = generate_providers(seed=42)
        towns: dict[str, int] = {}
        for p in providers:
            towns[p.town] = towns.get(p.town, 0) + 1
        assert len(towns) >= 8, "At least 8 towns required"
        for town, count in towns.items():
            assert 8 <= count <= 20, f"{town} has {count} providers, expected 8–20"

    def test_price_range(self) -> None:
        providers = generate_providers(seed=42)
        for p in providers:
            assert 2200 <= p.list_price_monthly <= 3800, f"{p.id}: price {p.list_price_monthly}"

    def test_capacity_range(self) -> None:
        providers = generate_providers(seed=42)
        for p in providers:
            assert 15 <= p.capacity_total <= 120
            assert 0 <= p.capacity_available <= p.capacity_total

    def test_every_provider_has_dishes_per_slot(self) -> None:
        providers = generate_providers(seed=42)
        for p in providers:
            slots = {d.slot for d in p.dishes}
            assert "lunch" in slots, f"{p.id} has no lunch dishes"
            assert "dinner" in slots, f"{p.id} has no dinner dishes"

    def test_dish_count_range(self) -> None:
        providers = generate_providers(seed=42)
        for p in providers:
            assert len(p.dishes) >= 2, f"{p.id} has only {len(p.dishes)} dishes"

    def test_all_approved(self) -> None:
        providers = generate_providers(seed=42)
        for p in providers:
            assert p.status == "approved"


class TestPhoneNumbers:
    """Phone numbers must use the obviously-fake format."""

    def test_all_phones_are_fake(self) -> None:
        providers = generate_providers(seed=42)
        for p in providers:
            assert p.phone is not None
            assert validate_phone_is_fake(p.phone), f"Phone looks real: {p.phone}"

    def test_no_real_indian_mobile(self) -> None:
        """No generated phone should match a real Indian mobile pattern (+91 [6-9]...)."""
        providers = generate_providers(seed=42)
        real_pattern = re.compile(r"^\+91\s?[6-9]\d{9}$")
        for p in providers:
            assert p.phone is not None
            cleaned = p.phone.replace(" ", "")
            assert not real_pattern.match(cleaned), f"Phone looks real: {p.phone}"

    def test_validate_phone_is_fake_rejects_real(self) -> None:
        assert not validate_phone_is_fake("+91 98765 43210")
        assert not validate_phone_is_fake("+91 70001 23456")

    def test_validate_phone_is_fake_accepts_fake(self) -> None:
        assert validate_phone_is_fake("+91 00000 01234")
        assert validate_phone_is_fake("+91 00000 09999")


class TestClusterProperties:
    """Every generated cluster must satisfy invariants."""

    def test_cluster_count_per_town(self) -> None:
        clusters = generate_clusters(seed=42)
        towns: dict[str, int] = {}
        for c in clusters:
            towns[c.town] = towns.get(c.town, 0) + 1
        for town, count in towns.items():
            assert 2 <= count <= 4, f"{town} has {count} clusters, expected 2–4"

    def test_cuisine_weights_sum_to_one(self) -> None:
        clusters = generate_clusters(seed=42)
        for c in clusters:
            total = sum(c.cuisine_weights.values())
            assert math.isclose(total, 1.0, abs_tol=0.01), f"{c.id}: cuisine weights sum to {total}"

    def test_diet_split_sums_to_one(self) -> None:
        clusters = generate_clusters(seed=42)
        for c in clusters:
            total = sum(c.diet_split.values())
            assert math.isclose(total, 1.0, abs_tol=0.01), f"{c.id}: diet split sums to {total}"

    def test_headcount_range(self) -> None:
        clusters = generate_clusters(seed=42)
        for c in clusters:
            assert 8 <= c.headcount <= 80

    def test_budget_range(self) -> None:
        clusters = generate_clusters(seed=42)
        for c in clusters:
            assert 2000 <= c.budget_ceiling_monthly <= 3500


class TestTownCoverage:
    """The required 8 towns must appear."""

    REQUIRED_TOWNS = {
        "Uluberia",
        "Howrah",
        "Kolkata",
        "Durgapur",
        "Kharagpur",
        "Medinipur",
        "Siliguri",
        "Asansol",
    }

    def test_all_towns_have_providers(self) -> None:
        providers = generate_providers(seed=42)
        towns = {p.town for p in providers}
        assert self.REQUIRED_TOWNS.issubset(towns)

    def test_all_towns_have_clusters(self) -> None:
        clusters = generate_clusters(seed=42)
        towns = {c.town for c in clusters}
        assert self.REQUIRED_TOWNS.issubset(towns)
