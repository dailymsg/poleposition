from collections.abc import Callable
from typing import Any, TypeVar

from {{package_name}}.bootstrap.logging import get_logger
from {{package_name}}.settings import get_settings


logger = get_logger(__name__)
ResultT = TypeVar("ResultT")


def enqueue_job(
    queue,
    function: Callable[..., ResultT],
    *args: Any,
    timeout_seconds: int | None = None,
    result_ttl_seconds: int | None = None,
    **kwargs: Any,
):
    settings = get_settings()
    job = queue.enqueue(
        function,
        *args,
        job_timeout=timeout_seconds or settings.rq_job_timeout_seconds,
        result_ttl=result_ttl_seconds or settings.rq_result_ttl_seconds,
        **kwargs,
    )
    logger.info(
        "Enqueued RQ job",
        extra={"job_id": getattr(job, "id", None), "queue_name": queue.name},
    )
    return job
