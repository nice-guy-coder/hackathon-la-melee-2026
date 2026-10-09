from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from app.api.deps import get_service
from app.services.search_service import SearchService

router = APIRouter(tags=["health"])


@router.get("/health")
def health(response: Response, service: SearchService = Depends(get_service)) -> dict[str, object]:
    payload = service.health()
    if payload.get("status") != "ok":
        response.status_code = 503
    return payload
