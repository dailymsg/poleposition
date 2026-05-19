# Redis Integration

Add Redis helpers to an existing PolePosition project:

```bash
polepos add integration redis
```

The command creates:

```text
src/<package>/integrations/redis/
  __init__.py
  cache.py
  factory.py
  schemas.py
  testing.py
```

It also updates:

- `src/<package>/settings.py`
- `.env.example`
- `pyproject.toml`

## Dependency

The command adds:

```text
redis>=5.0.0
```

Sync dependencies after adding the integration:

```bash
uv sync --extra dev
```

## Settings

Review the Redis values in `.env`:

```env
REDIS_ENABLED=false
REDIS_URL=redis://localhost:6379/0
REDIS_CLIENT_NAME=<package>
REDIS_KEY_PREFIX=<package>
REDIS_SOCKET_TIMEOUT_SECONDS=5.0
```

Required Redis values should remain active in `.env.example`. A commented
required value such as `# REDIS_URL=redis://localhost:6379/0` is treated as
missing by `polepos check`.

## Use the Cache

The generated factory builds an async Redis cache helper from settings:

```python
from <package>.integrations.redis import build_redis_cache

cache = build_redis_cache()
await cache.set_text("health", "ok", ttl_seconds=60)
value = await cache.get_text("health")
```

Use Redis for shared process-external cache state. For in-process-only state,
`polepos.data` structures may be enough.

For a complete cache-aside walkthrough, see the
[Redis Cache example](../examples/redis-cache.md).

## Testing

Use `build_in_memory_redis_cache()` from `testing.py` when unit tests should
assert cache behavior without connecting to Redis.
