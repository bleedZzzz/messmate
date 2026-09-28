"""FastAPI application factory and entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_health import router as health_router
from app.config import get_settings


def create_app() -> FastAPI:
    """Create and configure the FastAPI application instance."""
    settings = get_settings()

    application = FastAPI(
        title="Tiffin Optimizer API",
        version="0.1.0",
        description="Multi-agent AI backend for matching students with tiffin services.",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS configuration
    origins = [settings.frontend_origin] if settings.frontend_origin else ["*"]
    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers under /api/v1 prefix
    application.include_router(health_router, prefix="/api/v1")

    return application


app = create_app()
