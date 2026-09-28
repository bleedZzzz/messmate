"""Routes for localities and demand cluster exploration."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import check_rate_limit, get_db
from app.api.schemas import AreaItem, AreasResponse
from app.db.repositories import get_all_clusters

router = APIRouter(tags=["areas"])


@router.get(
    "/areas",
    response_model=AreasResponse,
    dependencies=[Depends(check_rate_limit)],
    summary="List towns and areas",
    description="Returns towns and localities with available demand clusters.",
)
def list_areas(db: Annotated[Session, Depends(get_db)]) -> AreasResponse:
    """Retrieve all available service localities grouped by town."""
    clusters = get_all_clusters(db)

    areas = [
        AreaItem(
            id=c.id,
            town=c.town,
            area=c.area,
            cluster_id=c.id,
            lat=c.lat,
            lon=c.lon,
            headcount=c.headcount,
        )
        for c in clusters
    ]

    towns = sorted({c.town for c in clusters})

    return AreasResponse(areas=areas, towns=towns)
