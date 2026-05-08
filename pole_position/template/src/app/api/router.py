from fastapi import APIRouter

from {{project_import_name}}.modules.status.router import router as status_router
# polepos:router-imports


api_router = APIRouter()
api_router.include_router(status_router, tags=["status"])
# polepos:router-includes
