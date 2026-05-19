from fastapi import APIRouter, Request

from redis_cache.modules.status.schemas import StatusResponse
from redis_cache.modules.status.services import get_status


router = APIRouter()


@router.get("/status", response_model=StatusResponse)
async def status(request: Request) -> StatusResponse:
    return get_status(request.app)
