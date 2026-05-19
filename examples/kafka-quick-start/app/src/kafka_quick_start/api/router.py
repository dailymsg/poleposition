from fastapi import APIRouter
from kafka_quick_start.modules.greetings.router import router as greetings_router
from kafka_quick_start.modules.status.router import router as status_router
# polepos:router-imports


api_router = APIRouter()
api_router.include_router(status_router, tags=["status"])
api_router.include_router(greetings_router, prefix="/greetings", tags=["greetings"])
# polepos:router-includes
