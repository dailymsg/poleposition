from contextvars import ContextVar, Token
import json
import logging
import sys
from datetime import datetime, timezone
from urllib.parse import urlparse


_request_id_context = ContextVar("request_id", default="-")


def bind_request_id(request_id: str) -> Token:
    return _request_id_context.set(request_id)


def reset_request_id(token: Token) -> None:
    _request_id_context.reset(token)


def get_request_id() -> str:
    return _request_id_context.get()


class DefaultFieldsFilter(logging.Filter):
    def __init__(self, *, app_name: str, environment: str) -> None:
        super().__init__()
        self.app_name = app_name
        self.environment = environment

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "app_name"):
            record.app_name = self.app_name
        if not hasattr(record, "environment"):
            record.environment = self.environment
        if not hasattr(record, "request_id"):
            record.request_id = get_request_id()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(
                record.created,
                tz=timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "app_name": getattr(record, "app_name", "-"),
            "environment": getattr(record, "environment", "-"),
            "request_id": getattr(record, "request_id", "-"),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def render_startup_table(
    *,
    app_name: str,
    app_env: str,
    app_debug: bool,
    api_v1_prefix: str,
    app_host: str,
    app_port: int,
    app_reload: bool,
    uvicorn_workers: int,
    database_url: str | None = None,
) -> str:
    display_host = "127.0.0.1" if app_host == "0.0.0.0" else app_host
    docs_url = f"http://{display_host}:{app_port}/docs"
    openapi_url = f"http://{display_host}:{app_port}/openapi.json"

    rows = [
        ("Service", app_name),
        ("Environment", app_env),
        ("Debug", str(app_debug).lower()),
        ("API Prefix", api_v1_prefix),
        ("Host", app_host),
        ("Port", str(app_port)),
        ("Reload", str(app_reload).lower()),
        ("Workers", str(uvicorn_workers)),
        ("Docs", docs_url),
        ("OpenAPI", openapi_url),
    ]
    if database_url:
        rows.insert(4, ("Database", urlparse(database_url).scheme or "unknown"))

    key_width = max(len("Setting"), *(len(key) for key, _ in rows))
    value_width = max(len("Value"), *(len(value) for _, value in rows))
    border = f"+-{'-' * key_width}-+-{'-' * value_width}-+"

    lines = [
        "PolePosition Startup",
        border,
        f"| {'Setting'.ljust(key_width)} | {'Value'.ljust(value_width)} |",
        border,
    ]
    lines.extend(
        f"| {key.ljust(key_width)} | {value.ljust(value_width)} |" for key, value in rows
    )
    lines.append(border)
    return "\n".join(lines)


def print_startup_table(**kwargs: object) -> None:
    print(render_startup_table(**kwargs), file=sys.stdout, flush=True)


def _build_formatter(log_format: str) -> logging.Formatter:
    if log_format.lower() == "json":
        return JsonFormatter()

    return logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "app=%(app_name)s env=%(environment)s request_id=%(request_id)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def setup_logging(
    *,
    log_level: str = "INFO",
    log_format: str = "text",
    app_name: str = "-",
    environment: str = "-",
) -> None:
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(log_level.upper())

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level.upper())
    handler.setFormatter(_build_formatter(log_format))
    handler.addFilter(
        DefaultFieldsFilter(
            app_name=app_name,
            environment=environment,
        )
    )

    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        named_logger = logging.getLogger(logger_name)
        named_logger.handlers.clear()
        named_logger.propagate = True
