from datetime import datetime, timezone

from fastapi import FastAPI

from openai_prompt import __version__
from openai_prompt.bootstrap.logging import get_logger
from openai_prompt.modules.status.schemas import StatusResponse
from openai_prompt.settings import get_settings


logger = get_logger(__name__)


def get_status(app: FastAPI) -> StatusResponse:
    settings = get_settings()
    started_at = getattr(app.state, "started_at", datetime.now(timezone.utc))
    now = datetime.now(timezone.utc)

    logger.info(
        "Status endpoint called",
        extra={
            "app_name": settings.app_name,
            "environment": settings.app_env,
        },
    )

    return StatusResponse(
        status="ok",
        service=settings.app_name,
        environment=settings.app_env,
        version=__version__,
        uptime_seconds=max(int((now - started_at).total_seconds()), 0),
        timestamp=now,
    )
