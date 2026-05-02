from pydantic import BaseModel


class LLMTextResult(BaseModel):
    text: str
    provider: str
    model: str
