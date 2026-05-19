from fastapi.testclient import TestClient

from redis_cache.integrations.redis.testing import build_in_memory_redis_cache
from redis_cache.modules.quotes import router as quotes_router


def test_read_quote_uses_cache(client: TestClient, monkeypatch) -> None:
    cache = build_in_memory_redis_cache(key_prefix="test")
    monkeypatch.setattr(quotes_router, "build_redis_cache", lambda: cache)

    first_response = client.get("/api/v1/quotes/fastapi")
    second_response = client.get("/api/v1/quotes/fastapi")

    assert first_response.status_code == 200
    assert first_response.json() == {
        "topic": "fastapi",
        "quote": "Build the smallest useful fastapi system first.",
        "cache": "miss",
    }
    assert second_response.status_code == 200
    assert second_response.json() == {
        "topic": "fastapi",
        "quote": "Build the smallest useful fastapi system first.",
        "cache": "hit",
    }
