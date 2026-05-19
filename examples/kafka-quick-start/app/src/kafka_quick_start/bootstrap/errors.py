from fastapi import FastAPI
from fastapi.responses import JSONResponse

from kafka_quick_start.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    NotFoundError,
)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def handle_not_found(_, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(AuthenticationError)
    async def handle_authentication_error(_, exc: AuthenticationError) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(AuthorizationError)
    async def handle_authorization_error(_, exc: AuthorizationError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    @app.exception_handler(DomainError)
    async def handle_domain_error(_, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
