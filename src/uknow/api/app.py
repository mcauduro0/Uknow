"""
FastAPI application factory.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from uknow.api.routes import health, tasks, webhooks
from uknow.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger = structlog.get_logger()
    logger.info("UKNOW API starting up")

    # Startup tasks
    yield

    # Shutdown tasks
    logger.info("UKNOW API shutting down")


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI app
    """
    settings = get_settings()

    app = FastAPI(
        title="UKNOW API",
        description="Multi-Agent AI Research and Business Intelligence System",
        version="0.1.0",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.is_development else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router, tags=["Health"])
    app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])

    return app


# Create default app instance
app = create_app()
