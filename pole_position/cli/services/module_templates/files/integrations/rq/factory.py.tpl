from {{package_name}}.settings import get_settings


def build_rq_queue(queue_name: str | None = None):
    settings = get_settings()

    try:
        from redis import Redis
        from rq import Queue
    except ImportError as exc:
        raise RuntimeError(
            "RQ integration requires rq. Run `uv sync` after "
            "`polepos add integration rq`."
        ) from exc

    connection = Redis.from_url(settings.rq_redis_url)
    return Queue(queue_name or settings.rq_default_queue, connection=connection)


def build_rq_worker(queue_names: list[str] | None = None):
    settings = get_settings()

    try:
        from redis import Redis
        from rq import Queue, Worker
    except ImportError as exc:
        raise RuntimeError(
            "RQ integration requires rq. Run `uv sync` after "
            "`polepos add integration rq`."
        ) from exc

    connection = Redis.from_url(settings.rq_redis_url)
    queues = [
        Queue(queue_name, connection=connection)
        for queue_name in (queue_names or [settings.rq_default_queue])
    ]
    return Worker(queues, connection=connection, name=settings.rq_worker_name)
