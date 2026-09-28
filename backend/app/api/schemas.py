"""Pydantic request and response schemas for FastAPI endpoints."""

from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.models.domain import DemandCluster, Diet, ProviderMatch


class ErrorDetail(BaseModel):
    """Structured error object."""

    code: str
    message: str


class ErrorResponse(BaseModel):
    """Standardized API error envelope (ARCHITECTURE.md §15)."""

    error: ErrorDetail


class AreaItem(BaseModel):
    """Summary of a locality with its associated demand cluster."""

    id: str
    town: str
    area: str
    cluster_id: str
    lat: float
    lon: float
    headcount: int


class AreasResponse(BaseModel):
    """Response model for GET /areas."""

    areas: list[AreaItem]
    towns: list[str]


class MatchRequest(BaseModel):
    """Request payload for POST /match."""

    area: str | None = None
    cluster_id: str | None = None
    lat: float | None = None
    lon: float | None = None
    radius_km: float = Field(default=5.0, gt=0)
    diet: Diet | None = None
    budget_max: float | None = None
    top_n: int = Field(default=5, ge=1, le=50)


class MatchResponse(BaseModel):
    """Response payload for POST /match."""

    cluster: DemandCluster
    matches: list[ProviderMatch]


class MenuRequest(BaseModel):
    """Request payload for POST /menu."""

    provider_id: str = Field(..., min_length=1)
    cluster_id: str = Field(..., min_length=1)


class NegotiateRequest(BaseModel):
    """Request payload for POST /negotiate."""

    provider_id: str = Field(..., min_length=1)
    cluster_id: str = Field(..., min_length=1)
    max_rounds: int = Field(default=5, ge=1, le=10)


class DishCreate(BaseModel):
    """Dish input for provider onboarding."""

    name: str = Field(..., min_length=2, max_length=100)
    slot: Literal["lunch", "dinner"]
    diet: Diet
    cuisine: str = Field(..., min_length=2, max_length=50)
    main_item: str = Field(..., min_length=2, max_length=50)
    cost_tier: Literal[1, 2, 3] = 2


class ProviderOnboardingRequest(BaseModel):
    """Request schema for POST /providers (Provider onboarding)."""

    name: str = Field(..., min_length=2, max_length=100)
    town: str = Field(..., min_length=2, max_length=100)
    area: str = Field(..., min_length=2, max_length=100)
    lat: float = Field(..., ge=-90.0, le=90.0)
    lon: float = Field(..., ge=-180.0, le=180.0)
    cuisines: list[str] = Field(..., min_length=1)
    diet_types: list[Diet] = Field(..., min_length=1)
    capacity_total: int = Field(..., gt=0)
    capacity_available: int = Field(..., ge=0)
    list_price_monthly: float = Field(..., gt=0)
    cost_per_meal: float = Field(..., gt=0)
    min_margin: float = Field(..., ge=0.0, le=1.0)
    flexibility: float = Field(..., ge=0.0, le=1.0)
    phone: str = Field(..., min_length=8, max_length=25)
    consent_given: bool = Field(...)
    dishes: list[DishCreate] = Field(default_factory=list)

    @field_validator("consent_given")
    @classmethod
    def validate_consent(cls, value: bool) -> bool:
        """Explicit consent is required for provider onboarding (PRD §7)."""
        if not value:
            raise ValueError("Explicit consent is required to register a provider.")
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        """Validate phone has at least 8 digits."""
        digits = re.sub(r"\D", "", value)
        if len(digits) < 8:
            raise ValueError("Phone number must contain at least 8 digits.")
        return value


class ProviderOnboardingResponse(BaseModel):
    """Response model for successful provider onboarding."""

    id: str
    status: Literal["pending"] = "pending"
    message: str


class ContactResponse(BaseModel):
    """Response model for GET /providers/{id}/contact (PRD FR-27)."""

    provider_id: str
    whatsapp_url: str
