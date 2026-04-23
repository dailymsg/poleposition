import logging

from fastapi import APIRouter

from {{project_name}} import __version__
from {{project_name}}.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
async def status() -> dict[str, str]:
    logger.info("Status endpoint called")

    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "version": __version__,
    }