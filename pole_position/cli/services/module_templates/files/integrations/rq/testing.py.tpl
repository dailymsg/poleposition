from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4


@dataclass
class InMemoryRqJob:
    id: str
    function_name: str
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
    result: Any = None
    status: str = "queued"


@dataclass
class InMemoryRqQueue:
    name: str = "test"
    jobs: list[InMemoryRqJob] = field(default_factory=list)
    execute_immediately: bool = False

    def enqueue(
        self,
        function: Callable[..., Any],
        *args: Any,
        job_timeout: int | None = None,
        result_ttl: int | None = None,
        **kwargs: Any,
    ) -> InMemoryRqJob:
        result = function(*args, **kwargs) if self.execute_immediately else None
        status = "finished" if self.execute_immediately else "queued"
        job = InMemoryRqJob(
            id=str(uuid4()),
            function_name=getattr(function, "__name__", repr(function)),
            args=args,
            kwargs={
                **kwargs,
                "job_timeout": job_timeout,
                "result_ttl": result_ttl,
            },
            result=result,
            status=status,
        )
        self.jobs.append(job)
        return job
