from fastapi import APIRouter
from openai_prompt.modules.assistant.router import router as assistant_router
from openai_prompt.modules.status.router import router as status_router
# polepos:router-imports


api_router = APIRouter()
api_router.include_router(status_router, tags=["status"])
api_router.include_router(assistant_router, prefix="/assistant", tags=["assistant"])
# polepos:router-includes
