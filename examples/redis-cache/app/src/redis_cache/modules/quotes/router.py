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
