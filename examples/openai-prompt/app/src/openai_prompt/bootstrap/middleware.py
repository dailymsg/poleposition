from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from openai_prompt.bootstrap.logging import bind_request_id, reset_request_id
from openai_prompt.settings import get_settings


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers") or [])
        raw_request_id = headers.get(b"x-request-id")
        request_id = raw_request_id.decode("latin-1") if raw_request_id else str(uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        token = bind_request_id(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                response_headers = [
                    (key, value)
                    for key, value in message.get("headers", [])
                    if key.lower() != b"x-request-id"
                ]
                response_headers.append((b"x-request-id", request_id.encode("latin-1")))
                message["headers"] = response_headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            reset_request_id(token)


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

    app.add_middleware(RequestContextMiddleware)
