"""FastAPI application factory, middleware, exception handlers, and routing."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.deps import get_session_factory
from app.api.middleware import RequestIdMiddleware
from app.api.routes_areas import router as areas_router
from app.api.routes_deal import router as deal_router
from app.api.routes_health import router as health_router
from app.api.routes_match import router as match_router
from app.api.routes_menu import router as menu_router
from app.api.routes_optimize import router as optimize_router
from app.api.routes_providers import router as providers_router
from app.config import get_settings
from app.data.seed import seed_database
from app.db.base import Base, build_engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Lifespan event handler: create tables and seed synthetic data on startup."""
    try:
        engine = build_engine()
        Base.metadata.create_all(bind=engine)
        factory = get_session_factory()
        with factory() as session:
            seed_database(session)
    except Exception as exc:
        logger.warning("Startup database check/seed encountered warning: %s", exc)
    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    application = FastAPI(
        title="Tiffin Optimizer API",
        version="0.1.0",
        description="Multi-agent AI backend for matching students with tiffin services.",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Request-ID Middleware
    application.add_middleware(RequestIdMiddleware)

    # 2. CORS configuration (PRD §7 & ARCHITECTURE.md §15)
    origins = [settings.frontend_origin] if settings.frontend_origin else ["*"]
    if settings.app_env == "local":
        origins = ["*"]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 3. Standardized Error Exception Handlers
    @application.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        code_map = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            422: "UNPROCESSABLE_ENTITY",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
        }
        code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": code, "message": str(exc.detail)}},
            headers=exc.headers,
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        err_details = []
        for error in exc.errors():
            loc = " -> ".join(str(item) for item in error.get("loc", []))
            msg = error.get("msg", "Invalid value")
            err_details.append(f"{loc}: {msg}")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "; ".join(err_details),
                }
            },
        )

    # 4. Include all routers under /api/v1 prefix
    application.include_router(health_router, prefix="/api/v1")
    application.include_router(areas_router, prefix="/api/v1")
    application.include_router(match_router, prefix="/api/v1")
    application.include_router(providers_router, prefix="/api/v1")
    application.include_router(menu_router, prefix="/api/v1")
    application.include_router(deal_router, prefix="/api/v1")
    application.include_router(optimize_router, prefix="/api/v1")

    return application


app = create_app()
