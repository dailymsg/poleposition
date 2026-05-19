from fastapi import FastAPI

from rabbitmq_quick_start.api.router import api_router
from rabbitmq_quick_start.bootstrap.errors import add_exception_handlers
from rabbitmq_quick_start.bootstrap.lifespan import lifespan
from rabbitmq_quick_start.bootstrap.logging import setup_logging
from rabbitmq_quick_start.bootstrap.middleware import add_middleware
from rabbitmq_quick_start.settings import get_settings


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
