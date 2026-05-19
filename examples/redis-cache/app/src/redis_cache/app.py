from fastapi import FastAPI

from redis_cache.api.router import api_router
from redis_cache.bootstrap.errors import add_exception_handlers
from redis_cache.bootstrap.lifespan import lifespan
from redis_cache.bootstrap.logging import setup_logging
from redis_cache.bootstrap.middleware import add_middleware
from redis_cache.settings import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(
        log_level=settings.log_level,
        log_format=settings.log_format,
        app_name=settings.app_name,
        environment=settings.app_env,
    )

    application = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        lifespan=lifespan,
    )
    add_middleware(application)
    add_exception_handlers(application)
    application.include_router(api_router, prefix=settings.api_v1_prefix)
    return application
