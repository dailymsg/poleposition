import asyncio

from redis_cache.integrations.redis.testing import build_in_memory_redis_cache
from redis_cache.modules.quotes.services.quotes_service import get_quote


def test_get_quote_caches_after_first_lookup() -> None:
    cache = build_in_memory_redis_cache(key_prefix="test")

    first_quote, first_status = asyncio.run(get_quote(cache, topic="fastapi"))
    second_quote, second_status = asyncio.run(get_quote(cache, topic="fastapi"))

    assert first_quote == "Build the smallest useful fastapi system first."
    assert second_quote == first_quote
    assert first_status == "miss"
    assert second_status == "hit"
