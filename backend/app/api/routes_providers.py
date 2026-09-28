"""Routes for provider details, onboarding, and contact redirection."""

from __future__ import annotations

import re
import urllib.parse
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import check_rate_limit, get_db
from app.api.schemas import (
    ContactResponse,
    ProviderOnboardingRequest,
    ProviderOnboardingResponse,
)
from app.db import repositories
from app.models.domain import Dish, Provider

router = APIRouter(tags=["providers"])


def _slugify(text: str) -> str:
    """Normalize text into URL-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "local"


@router.get(
    "/providers/{provider_id}",
    response_model=Provider,
    dependencies=[Depends(check_rate_limit)],
    summary="Get provider details",
    description="Returns detailed provider profile including dish catalog.",
)
def get_provider_details(
    provider_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> Provider:
    """Fetch single provider by ID."""
    provider = repositories.get_provider_by_id(db, provider_id)
    if provider is None:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_id}' not found",
        )
    return provider


@router.post(
    "/providers",
    response_model=ProviderOnboardingResponse,
    status_code=201,
    dependencies=[Depends(check_rate_limit)],
    summary="Submit provider onboarding",
    description="Registers a new provider with 'pending' status. Requires explicit consent.",
)
def onboard_provider(
    payload: ProviderOnboardingRequest,
    db: Annotated[Session, Depends(get_db)],
) -> ProviderOnboardingResponse:
    """Create pending provider record with dishes."""
    town_slug = _slugify(payload.town)
    area_slug = _slugify(payload.area)
    unique_suffix = uuid.uuid4().hex[:6]
    provider_id = f"{town_slug}-{area_slug}-p{unique_suffix}"

    dishes = [
        Dish(
            id=f"{provider_id}-dish-{idx:03d}",
            name=d.name,
            slot=d.slot,
            diet=d.diet,
            cuisine=d.cuisine,
            main_item=d.main_item,
            cost_tier=d.cost_tier,
        )
        for idx, d in enumerate(payload.dishes, start=1)
    ]

    provider = Provider(
        id=provider_id,
        name=payload.name,
        town=payload.town,
        area=payload.area,
        lat=payload.lat,
        lon=payload.lon,
        cuisines=payload.cuisines,
        diet_types=payload.diet_types,
        capacity_total=payload.capacity_total,
        capacity_available=payload.capacity_available,
        list_price_monthly=payload.list_price_monthly,
        cost_per_meal=payload.cost_per_meal,
        min_margin=payload.min_margin,
        flexibility=payload.flexibility,
        rating=4.0,  # Default starter rating for new onboarding
        dishes=dishes,
        phone=payload.phone,
        status="pending",
    )

    repositories.insert_provider(db, provider, consent=payload.consent_given)
    db.commit()

    return ProviderOnboardingResponse(
        id=provider.id,
        status="pending",
        message="Provider registration submitted successfully. Status is pending approval.",
    )


@router.get(
    "/providers/{provider_id}/contact",
    response_model=ContactResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="Get WhatsApp contact link",
    description="Returns a wa.me direct link with a pre-filled subscription inquiry.",
)
def get_provider_contact(
    provider_id: str,
    db: Annotated[Session, Depends(get_db)],
) -> ContactResponse:
    """Generate WhatsApp contact URL (PRD FR-27, no phone numbers logged)."""
    provider = repositories.get_provider_by_id(db, provider_id)
    if provider is None:
        raise HTTPException(
            status_code=404,
            detail=f"Provider '{provider_id}' not found",
        )

    raw_phone = provider.phone or ""
    clean_digits = re.sub(r"\D", "", raw_phone)
    if not clean_digits:
        raise HTTPException(
            status_code=400,
            detail="Provider has no valid contact phone number.",
        )

    prefilled_text = (
        f"Hello {provider.name}, I found your mess service on Tiffin Optimizer "
        "and would like to inquire about monthly tiffin subscription."
    )
    encoded_text = urllib.parse.quote(prefilled_text)
    whatsapp_url = f"https://wa.me/{clean_digits}?text={encoded_text}"

    return ContactResponse(
        provider_id=provider.id,
        whatsapp_url=whatsapp_url,
    )
