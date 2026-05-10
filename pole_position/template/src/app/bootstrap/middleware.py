from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from {{project_import_name}}.bootstrap.logging import bind_request_id, reset_request_id
from {{project_import_name}}.settings import get_settings


def add_middleware(app: FastAPI) -> None:
    settings = get_settings()

    if settings.cors_enabled:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allow_origins,
            allow_origin_regex=settings.cors_allow_origin_regex,
            allow_credentials=settings.cors_allow_credentials,
            allow_methods=settings.cors_allow_methods,
            allow_headers=settings.cors_allow_headers,
            expose_headers=settings.cors_expose_headers,
            max_age=settings.cors_max_age,
        )

    @app.middleware("http")
    async def attach_request_context(request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid4())
        request.state.request_id = request_id
        token = bind_request_id(request_id)

        try:
            response = await call_next(request)
            response.headers["x-request-id"] = request_id
            return response
        finally:
            reset_request_id(token)
