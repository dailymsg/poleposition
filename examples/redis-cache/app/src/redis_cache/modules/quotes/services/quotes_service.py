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
