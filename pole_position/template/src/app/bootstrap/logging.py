import logging
import sys
from urllib.parse import urlparse


class DefaultFieldsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "app_name"):
            record.app_name = "-"
        if not hasattr(record, "environment"):
            record.environment = "-"
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def render_startup_table(
    *,
    app_name: str,
    app_env: str,
    app_debug: bool,
    api_v1_prefix: str,
    database_url: str,
    app_host: str,
    app_port: int,
    app_reload: bool,
    uvicorn_workers: int,
) -> str:
    display_host = "127.0.0.1" if app_host == "0.0.0.0" else app_host
    docs_url = f"http://{display_host}:{app_port}/docs"
    openapi_url = f"http://{display_host}:{app_port}/openapi.json"
    database_backend = urlparse(database_url).scheme or "unknown"

    rows = [
        ("Service", app_name),
        ("Environment", app_env),
        ("Debug", str(app_debug).lower()),
        ("API Prefix", api_v1_prefix),
        ("Database", database_backend),
        ("Host", app_host),
        ("Port", str(app_port)),
        ("Reload", str(app_reload).lower()),
        ("Workers", str(uvicorn_workers)),
        ("Docs", docs_url),
        ("OpenAPI", openapi_url),
    ]

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


def setup_logging(log_level: str = "INFO") -> None:
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.handlers.clear()

    root_logger.setLevel(log_level.upper())

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s | %(levelname)s | %(name)s | "
            "app=%(app_name)s env=%(environment)s request_id=%(request_id)s | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level.upper())
    handler.setFormatter(formatter)
    handler.addFilter(DefaultFieldsFilter())

    root_logger.addHandler(handler)

    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        named_logger = logging.getLogger(logger_name)
        named_logger.handlers.clear()
        named_logger.propagate = True
