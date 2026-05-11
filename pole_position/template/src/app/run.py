import uvicorn

from {{project_import_name}}.bootstrap.logging import print_startup_table
from {{project_import_name}}.settings import get_settings


settings = get_settings()


def main() -> None:
    print_startup_table(
        app_name=settings.app_name,
        app_env=settings.app_env,
        app_debug=settings.app_debug,
        api_v1_prefix=settings.api_v1_prefix,
        app_host=settings.app_host,
        app_port=settings.app_port,
        app_reload=settings.app_reload,
        uvicorn_workers=settings.uvicorn_workers,
        database_url=settings.database_url,
    )
    uvicorn.run(
        "{{project_import_name}}.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_reload,
        workers=settings.uvicorn_workers,
        log_level=settings.log_level.lower(),
        access_log=settings.uvicorn_access_log,
        proxy_headers=settings.uvicorn_proxy_headers,
        forwarded_allow_ips=settings.uvicorn_forwarded_allow_ips,
        server_header=settings.uvicorn_server_header,
        date_header=settings.uvicorn_date_header,
        use_colors=settings.uvicorn_use_colors,
        timeout_keep_alive=settings.uvicorn_timeout_keep_alive,
        timeout_graceful_shutdown=settings.uvicorn_timeout_graceful_shutdown,
        timeout_worker_healthcheck=settings.uvicorn_timeout_worker_healthcheck,
        limit_concurrency=settings.uvicorn_limit_concurrency,
        limit_max_requests=settings.uvicorn_limit_max_requests,
        limit_max_requests_jitter=settings.uvicorn_limit_max_requests_jitter,
        backlog=settings.uvicorn_backlog,
    )


if __name__ == "__main__":
    main()
