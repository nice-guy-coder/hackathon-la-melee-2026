from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_service
from app.schemas.recommendation import SearchResponse
from app.schemas.search import SearchRequest
from app.services.search_service import SearchService

router = APIRouter(prefix="/api", tags=["search"])


@router.post("/search", response_model=SearchResponse)
def search(
    payload: SearchRequest,
    service: SearchService = Depends(get_service),
) -> SearchResponse:
    return service.search(payload)
