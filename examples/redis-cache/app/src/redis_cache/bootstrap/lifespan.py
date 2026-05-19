from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI

from redis_cache.bootstrap.logging import get_logger
from redis_cache.settings import get_settings


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.started_at = datetime.now(timezone.utc)

    logger.info(
        "Application starting",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
        },
    )
    yield
    logger.info(
        "Application shutting down",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
        },
    )
