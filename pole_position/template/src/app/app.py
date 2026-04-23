import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from {{project_name}}.api.router import api_router
from {{project_name}}.core.config import settings
from {{project_name}}.core.logging import setup_logging


setup_logging(log_level=settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI):
    logger.info(
        "Application starting",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
        },
    )
    yield
    logger.info("Application shutting down")


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application


app = create_app()