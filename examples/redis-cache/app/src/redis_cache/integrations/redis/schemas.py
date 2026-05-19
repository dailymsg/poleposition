from pydantic import BaseModel, Field


class RedisCacheEntry(BaseModel):
    key: str = Field(min_length=1)
    value: str
    ttl_seconds: int | None = Field(default=None, gt=0)
