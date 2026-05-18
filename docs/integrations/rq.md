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
