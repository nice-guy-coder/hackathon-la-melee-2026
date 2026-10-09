from __future__ import annotations

from fastapi import Request

from app.services.search_service import SearchService


def get_service(request: Request) -> SearchService:
    return request.app.state.search_service
