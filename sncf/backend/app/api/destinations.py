from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.deps import get_service
from app.schemas.destination import Destination
from app.services.search_service import SearchService

router = APIRouter(prefix="/api", tags=["destinations"])


@router.get("/destinations", response_model=list[Destination])
def list_destinations(
    theme: str | None = Query(default=None, max_length=40),
    limit: int = Query(default=50, ge=1, le=100),
    service: SearchService = Depends(get_service),
) -> list[Destination]:
    return service.destinations(theme=theme, limit=limit)
