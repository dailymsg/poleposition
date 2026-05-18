# RQ Integration

Add Redis-backed background job helpers with:

```bash
polepos add integration rq
```

The command creates:

```text
src/<package>/integrations/rq/
  __init__.py
  factory.py
  jobs.py
  schemas.py
  testing.py
  worker.py
```

It also adds:

- dependency: `rq>=1.16.0`
- settings such as `rq_redis_url`, `rq_default_queue`, and
  `rq_job_timeout_seconds`
- `.env.example` values such as `RQ_REDIS_URL`, `RQ_DEFAULT_QUEUE`, and
  `RQ_JOB_TIMEOUT_SECONDS`

Use `build_rq_queue()` when application code needs to enqueue work, and
`run_worker()` from `worker.py` in an explicit worker process. PolePosition
does not start RQ workers inside the FastAPI API process.

Use `InMemoryRqQueue` from `testing.py` for unit tests that should capture
enqueued jobs without Redis.

## Enqueue a Job

Define job functions in normal application modules. Keep them importable by the
worker process.

```python
from <package>.integrations.rq import build_rq_queue, enqueue_job


def send_welcome_email(user_id: int) -> None:
    ...


queue = build_rq_queue()
job = enqueue_job(queue, send_welcome_email, 42)
```

`enqueue_job()` uses generated settings for default timeout and result TTL.
Override them per job when needed:

```python
enqueue_job(
    queue,
    send_welcome_email,
    42,
    timeout_seconds=60,
    result_ttl_seconds=300,
)
```

## Run a Worker

The generated `worker.py` exposes:

```python
from <package>.integrations.rq.worker import run_worker


run_worker()
```

In a real project, wrap this in a small script or process entrypoint owned by
your deployment. Keep it separate from the FastAPI API process so API startup
does not accidentally start background workers.

Example local worker module:

```python
from <package>.integrations.rq.worker import run_worker


def main() -> None:
    run_worker()


if __name__ == "__main__":
    main()
```

Then run it with the same environment as the API:

```bash
uv run python -m <package>.worker
```

## Configuration

Review generated values in `.env`:

```env
RQ_ENABLED=false
RQ_REDIS_URL=redis://localhost:6379/0
RQ_DEFAULT_QUEUE=<package>.default
RQ_WORKER_NAME=<package>-worker
RQ_JOB_TIMEOUT_SECONDS=300
RQ_RESULT_TTL_SECONDS=500
```

`RQ_ENABLED` is a project-level switch for application code. The generated
factory does not silently start workers when it is true; worker startup remains
explicit.

## Testing

Use `InMemoryRqQueue` for unit tests:

```python
from <package>.integrations.rq.jobs import enqueue_job
from <package>.integrations.rq.testing import InMemoryRqQueue


def test_enqueues_job() -> None:
    queue = InMemoryRqQueue()

    def task(value: int) -> int:
        return value + 1

    job = enqueue_job(queue, task, 1)

    assert job in queue.jobs
    assert job.status == "queued"
```

Use `execute_immediately=True` when the test should run the callable without a
Redis worker:

```python
queue = InMemoryRqQueue(execute_immediately=True)
```

## Validation

After adding RQ, run:

```bash
polepos check
uv sync
```

`polepos check` verifies generated RQ files, dependency, settings, and active
`.env.example` values. It does not connect to Redis.
