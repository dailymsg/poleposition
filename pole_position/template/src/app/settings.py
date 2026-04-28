from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "{{project_name}}"
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "INFO"
    api_v1_prefix: str = "/api/v1"
    database_url: str = Field(default="sqlite:///./poleposition.db")
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    app_reload: bool = True
    uvicorn_workers: int = 1
    uvicorn_access_log: bool = True
    uvicorn_proxy_headers: bool = True
    uvicorn_forwarded_allow_ips: str = "127.0.0.1"
    uvicorn_server_header: bool = True
    uvicorn_date_header: bool = True
    uvicorn_use_colors: bool | None = None
    uvicorn_timeout_keep_alive: int = 5
    uvicorn_timeout_graceful_shutdown: int | None = None
    uvicorn_timeout_worker_healthcheck: int = 5
    uvicorn_limit_concurrency: int | None = None
    uvicorn_limit_max_requests: int | None = None
    uvicorn_limit_max_requests_jitter: int = 0
    uvicorn_backlog: int = 2048

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator(
        "uvicorn_use_colors",
        "uvicorn_timeout_graceful_shutdown",
        "uvicorn_limit_concurrency",
        "uvicorn_limit_max_requests",
        mode="before",
    )
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if isinstance(value, str) and not value.strip():
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
