"""Pydantic domain models for Tiffin Optimizer.

Canonical definitions from ARCHITECTURE.md section 5.
All monetary values are in INR per person per month unless stated otherwise.
"""

from typing import Literal

from pydantic import BaseModel, Field

Diet = Literal["veg", "non_veg", "egg"]
MealSlot = Literal["lunch", "dinner"]


class Dish(BaseModel):
    """A single dish in a provider's catalog."""

    id: str
    name: str
    slot: MealSlot
    diet: Diet
    cuisine: str  # e.g. "bengali", "north_indian"
    main_item: str  # e.g. "fish", "dal", "paneer", "egg"
    cost_tier: Literal[1, 2, 3]


class Provider(BaseModel):
    """A tiffin/mess service provider."""

    id: str
    name: str
    town: str
    area: str
    lat: float
    lon: float
    cuisines: list[str]
    diet_types: list[Diet]
    capacity_total: int
    capacity_available: int
    list_price_monthly: float  # 2 meals/day plan
    cost_per_meal: float
    min_margin: float = Field(ge=0, le=1)  # e.g. 0.15
    flexibility: float = Field(gt=0, le=1)  # concession speed
    rating: float = Field(ge=0, le=5)
    dishes: list[Dish]
    phone: str | None = None
    status: Literal["pending", "approved"] = "approved"


class DemandCluster(BaseModel):
    """A geographic cluster of student/bachelor demand."""

    id: str
    town: str
    area: str
    lat: float
    lon: float
    headcount: int
    budget_ceiling_monthly: float
    cuisine_weights: dict[str, float]  # sums to 1
    diet_split: dict[Diet, float]  # sums to 1
    flexibility: float = Field(gt=0, le=1)


class ProviderMatch(BaseModel):
    """Result of matching a provider to a demand cluster."""

    provider_id: str
    score: float
    factors: dict[str, float]  # per-factor scores
    distance_km: float
    reason: str


class MealPick(BaseModel):
    """A single meal selection in a menu plan."""

    dish_id: str
    name: str


class DayMenu(BaseModel):
    """One day's menu with lunch and dinner."""

    day: int  # 1..7
    lunch: MealPick
    dinner: MealPick


class MenuPlan(BaseModel):
    """A 7-day menu plan for a provider-cluster pair."""

    provider_id: str
    cluster_id: str
    days: list[DayMenu]
    rationale: str
    source: Literal["llm", "fallback"]


class NegotiationRound(BaseModel):
    """One round of price negotiation."""

    round: int
    provider_ask: float
    cluster_bid: float


class NegotiationResult(BaseModel):
    """Outcome of a price negotiation simulation."""

    status: Literal["deal", "compromise", "no_deal"]
    final_price: float | None
    floor: float
    ceiling: float
    volume_discount: float
    rounds: list[NegotiationRound]
    note: str


class TraceStep(BaseModel):
    """Observability record for one agent step in the pipeline."""

    agent: str
    started_ms: int
    duration_ms: int
    used_llm: bool
    fallback_used: bool
    error: str | None = None
