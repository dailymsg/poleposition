from redis_cache.integrations.redis.cache import RedisCache


class InMemoryRedisClient:
    def __init__(self) -> None:
        self.values: dict[str, bytes | str] = {}
        self.closed = False

    async def get(self, name: str) -> bytes | str | None:
        return self.values.get(name)

    async def set(
        self,
        name: str,
        value: bytes | str,
        *,
        ex: int | None = None,
    ) -> bool:
        self.values[name] = value
        return True

    async def delete(self, *names: str) -> int:
        removed = 0
        for name in names:
            if name in self.values:
                removed += 1
                del self.values[name]
        return removed

    async def close(self) -> None:
        self.closed = True


def build_in_memory_redis_cache(*, key_prefix: str = "test") -> RedisCache:
    return RedisCache(InMemoryRedisClient(), key_prefix=key_prefix)
