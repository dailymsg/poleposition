from fastapi import APIRouter, Request

from openai_prompt.modules.status.schemas import StatusResponse
from openai_prompt.modules.status.services import get_status


router = APIRouter()


@router.get("/status", response_model=StatusResponse)
async def status(request: Request) -> StatusResponse:
    return get_status(request.app)
