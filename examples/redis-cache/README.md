# Redis Cache Scenario

This guide shows how to use PolePosition's Redis integration for a simple
cache-aside workflow.

Cache-aside means the application:

1. checks Redis first
2. returns the cached value on a hit
3. computes or loads the value on a miss
4. stores the value with a TTL for the next request

The PolePosition version uses:

- `polepos add integration redis` for the async Redis cache helper, settings,
  env values, dependency, and in-memory test helper
- `polepos add module quotes --api-only` for the HTTP boundary

## Complete Runnable Source

This example includes a complete PolePosition-generated project:

```text
examples/redis-cache/app/
```

Run it directly:

```bash
cd examples/redis-cache/app
cp .env.example .env
uv sync --extra dev
docker compose -f compose.redis.yaml up -d
uv run python -m redis_cache.run
```

The rest of this guide explains how that `app/` project was built and why each
file exists.

## Scenario Goal

Build a tiny cached API:

```text
GET /api/v1/quotes/{topic}
```

The first request computes a quote response and stores it in Redis. Repeated
requests for the same topic return the cached response.

## Step 1: Create the Project

This example does not need database wiring:

```bash
polepos start redis-cache --db none
cd redis-cache
cp .env.example .env
uv sync --extra dev
```

## Step 2: Add Redis

```bash
polepos add integration redis
uv sync --extra dev
```

PolePosition creates:

```text
src/redis_cache/integrations/redis/
  __init__.py
  cache.py
  factory.py
  schemas.py
  testing.py
```

Use these `.env` values:

```env
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379/0
REDIS_CLIENT_NAME=redis_cache
REDIS_KEY_PREFIX=redis_cache
REDIS_SOCKET_TIMEOUT_SECONDS=5.0
```

Why these settings matter:

- `REDIS_URL` points the generated client at Redis
- `REDIS_KEY_PREFIX` keeps this app's keys away from other apps in the same
  Redis database
- `REDIS_SOCKET_TIMEOUT_SECONDS` prevents cache calls from hanging forever

## Step 3: Run Redis Locally

Create `compose.redis.yaml`:

```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

Start Redis:

```bash
docker compose -f compose.redis.yaml up -d
```

## Step 4: Generate the Quotes Module

```bash
polepos add module quotes --api-only
```

PolePosition creates:

```text
src/redis_cache/modules/quotes/
  __init__.py
  router.py
  schemas.py
  services/
    __init__.py
    quotes_service.py
tests/integration/test_quotes.py
tests/unit/test_quotes_api_service.py
```

## Step 5: Define the API Schema

Replace `src/redis_cache/modules/quotes/schemas.py`:

```python
from pydantic import BaseModel


class QuoteResponse(BaseModel):
    topic: str
    quote: str
    cache: str
```

Why this file exists:

- the response tells callers whether they saw a cache hit or miss
- the API contract stays explicit even though Redis is an implementation detail

## Step 6: Implement Cache-Aside Logic

Replace `src/redis_cache/modules/quotes/services/quotes_service.py`:

```python
from typing import Protocol


class TextCache(Protocol):
    async def get_text(self, name: str) -> str | None:
        ...

    async def set_text(
        self,
        name: str,
        value: str,
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        ...


def _cache_key(topic: str) -> str:
    return f"quotes:{topic.lower()}"


def _load_quote(topic: str) -> str:
    normalized = topic.replace("-", " ")
    return f"Build the smallest useful {normalized} system first."


async def get_quote(
    cache: TextCache,
    *,
    topic: str,
    ttl_seconds: int = 300,
) -> tuple[str, str]:
    cached = await cache.get_text(_cache_key(topic))
    if cached is not None:
        return cached, "hit"

    quote = _load_quote(topic)
    await cache.set_text(_cache_key(topic), quote, ttl_seconds=ttl_seconds)
    return quote, "miss"
```

What this service does:

- it depends on a `Protocol`, so tests can use an in-memory cache
- it keeps key construction in one function
- it stores only text, which matches the generated Redis helper's simple API
- it uses a TTL so stale values eventually leave the cache

Replace `src/redis_cache/modules/quotes/router.py`:

```python
from fastapi import APIRouter

from redis_cache.integrations.redis.factory import build_redis_cache
from redis_cache.modules.quotes.schemas import QuoteResponse
from redis_cache.modules.quotes.services.quotes_service import get_quote


router = APIRouter()


@router.get("/{topic}", response_model=QuoteResponse)
async def read_quote(topic: str) -> QuoteResponse:
    cache = build_redis_cache()
    try:
        quote, cache_status = await get_quote(cache, topic=topic)
    finally:
        await cache.close()

    return QuoteResponse(topic=topic, quote=quote, cache=cache_status)
```

What this router does:

- it keeps Redis construction at the edge of the request
- it closes the Redis client after the tutorial request completes
- it returns cache status so the tutorial is easy to verify

For production traffic, create the Redis client during application startup and
reuse it through application lifespan or dependency injection.

## Step 7: Try It

Run FastAPI:

```bash
uv run python -m redis_cache.run
```

Call the endpoint twice:

```bash
curl http://localhost:8000/api/v1/quotes/fastapi
curl http://localhost:8000/api/v1/quotes/fastapi
```

The first response should include:

```json
{
  "topic": "fastapi",
  "quote": "Build the smallest useful fastapi system first.",
  "cache": "miss"
}
```

The second response should include:

```json
{
  "topic": "fastapi",
  "quote": "Build the smallest useful fastapi system first.",
  "cache": "hit"
}
```

Inspect the key directly:

```bash
docker compose -f compose.redis.yaml exec redis redis-cli GET redis_cache:quotes:fastapi
```

## Step 8: Test Without Redis

Replace `tests/unit/test_quotes_api_service.py`:

```python
import pytest

from redis_cache.integrations.redis.testing import build_in_memory_redis_cache
from redis_cache.modules.quotes.services.quotes_service import get_quote


@pytest.mark.asyncio
async def test_get_quote_caches_after_first_lookup() -> None:
    cache = build_in_memory_redis_cache(key_prefix="test")

    first_quote, first_status = await get_quote(cache, topic="fastapi")
    second_quote, second_status = await get_quote(cache, topic="fastapi")

    assert first_quote == "Build the smallest useful fastapi system first."
    assert second_quote == first_quote
    assert first_status == "miss"
    assert second_status == "hit"
```

Why this test is useful:

- it verifies the cache-aside behavior directly
- it does not require a running Redis container
- it still exercises the generated `RedisCache` helper through the in-memory
  client

Run:

```bash
uv run pytest
polepos check
```

## When To Use This Shape

Use this pattern for:

- expensive reads
- external API responses
- short-lived computed views
- feature flags or reference data that can tolerate brief staleness

Do not use cache-aside as the source of truth. Redis cache values should be
safe to rebuild after expiration or eviction.
