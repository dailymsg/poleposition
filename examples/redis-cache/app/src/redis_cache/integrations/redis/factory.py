from redis_cache.integrations.redis.cache import RedisCache
from redis_cache.settings import get_settings


def build_redis_cache() -> RedisCache:
    settings = get_settings()

    try:
        from redis.asyncio import from_url
    except ImportError as exc:
        raise RuntimeError(
            "Redis integration requires redis. Run `uv sync --extra dev` after "
            "`polepos add integration redis`."
        ) from exc

    client = from_url(
        settings.redis_url,
        client_name=settings.redis_client_name,
        socket_timeout=settings.redis_socket_timeout_seconds,
        decode_responses=False,
    )
    return RedisCache(client, key_prefix=settings.redis_key_prefix)
