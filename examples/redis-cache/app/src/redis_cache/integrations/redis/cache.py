from typing import Protocol

from redis_cache.bootstrap.logging import get_logger


logger = get_logger(__name__)


class RedisClient(Protocol):
    async def get(self, name: str) -> bytes | str | None:
        ...

    async def set(
        self,
        name: str,
        value: bytes | str,
        *,
        ex: int | None = None,
    ) -> object:
        ...

    async def delete(self, *names: str) -> int:
        ...

    async def close(self) -> object:
        ...


class RedisCache:
    def __init__(self, client: RedisClient, *, key_prefix: str = "") -> None:
        self.client = client
        self.key_prefix = key_prefix.strip(":")

    def key(self, name: str) -> str:
        normalized = name.strip(":")
        if not self.key_prefix:
            return normalized
        return f"{self.key_prefix}:{normalized}"

    async def get_text(self, name: str) -> str | None:
        value = await self.client.get(self.key(name))
        if value is None:
            return None
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    async def set_text(
        self,
        name: str,
        value: str,
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        await self.client.set(self.key(name), value, ex=ttl_seconds)
        logger.info("Stored Redis cache value", extra={"cache_key": self.key(name)})

    async def delete(self, *names: str) -> int:
        if not names:
            return 0
        return await self.client.delete(*(self.key(name) for name in names))

    async def close(self) -> None:
        await self.client.close()
