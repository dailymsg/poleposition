from fastapi import APIRouter
from redis_cache.modules.quotes.router import router as quotes_router
from redis_cache.modules.status.router import router as status_router
# polepos:router-imports


api_router = APIRouter()
api_router.include_router(status_router, tags=["status"])
api_router.include_router(quotes_router, prefix="/quotes", tags=["quotes"])
# polepos:router-includes
