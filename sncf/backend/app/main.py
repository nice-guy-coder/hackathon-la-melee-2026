from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api import compare, destinations, health, search
from app.config import Settings, get_settings
from app.data.base import DataSourceError
from app.data.factory import create_data_layer
from app.parsers.llm_parser import create_parser
from app.services.search_service import InputError, SearchService

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    logging.basicConfig(level=logging.INFO)

    app = FastAPI(
        title="SNCF Secure School Trip Planner",
        version=settings.app_version,
        docs_url="/docs" if settings.enable_docs else None,
        redoc_url=None,
        openapi_url="/openapi.json" if settings.enable_docs else None,
    )
    app.state.settings = settings

    data_layer = None
    try:
        data_layer = create_data_layer(settings)
    except DataSourceError:
        logger.exception("Data source '%s' could not be loaded.", settings.data_source)
    app.state.search_service = SearchService(
        data_layer=data_layer,
        parser=create_parser(settings),
        settings=settings,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
        max_age=600,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=list(settings.allowed_hosts))

    @app.middleware("http")
    async def guard_requests(request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length and content_length.isdigit():
            if int(content_length) > settings.max_request_bytes:
                return JSONResponse(status_code=413, content={"detail": "Request entity too large."})
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        if request.url.path.startswith("/api"):
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(DataSourceError)
    async def _data_source_unavailable(request: Request, exc: DataSourceError) -> JSONResponse:
        logger.warning("Data source error: %s", exc)
        return JSONResponse(status_code=503, content={"detail": "Data source unavailable."})

    @app.exception_handler(InputError)
    async def _invalid_input(request: Request, exc: InputError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error.")
        return JSONResponse(status_code=500, content={"detail": "Internal server error."})

    app.include_router(health.router)
    app.include_router(search.router)
    app.include_router(destinations.router)
    app.include_router(compare.router)
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    active = get_settings()
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=not active.is_production,
    )
