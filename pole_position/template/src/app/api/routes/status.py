import logging
import time

from fastapi import APIRouter

from app.core.config import settings

from app import __version__

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/status")
def status() -> dict:
    logger.info("Status endpoint called")

    return {
        "uptime": time.time(),
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "version": __version__
    }