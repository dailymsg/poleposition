from fastapi import APIRouter

from {{project_name}}.api.routes.status import router as status_router

api_router = APIRouter()
api_router.include_router(status_router, tags=["status"])