from pydantic import BaseModel


class QuoteResponse(BaseModel):
    topic: str
    quote: str
    cache: str
