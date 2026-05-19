from fastapi import FastAPI

from openai_prompt.api.router import api_router
from openai_prompt.bootstrap.errors import add_exception_handlers
from openai_prompt.bootstrap.lifespan import lifespan
from openai_prompt.bootstrap.logging import setup_logging
from openai_prompt.bootstrap.middleware import add_middleware
from openai_prompt.settings import get_settings


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
