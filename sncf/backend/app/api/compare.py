from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import get_service
from app.schemas.recommendation import CompareRequest, CompareResponse
from app.services.search_service import SearchService

router = APIRouter(prefix="/api", tags=["compare"])


@router.post("/compare", response_model=CompareResponse)
def compare(
    payload: CompareRequest,
    service: SearchService = Depends(get_service),
) -> CompareResponse:
    return service.compare(payload)
