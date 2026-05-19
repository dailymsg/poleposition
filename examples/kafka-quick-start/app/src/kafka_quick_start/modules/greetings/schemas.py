from pydantic import BaseModel, Field


class GreetingRequest(BaseModel):
    recipient: str = Field(default="team", min_length=1)
    message: str = Field(default="Hello, PolePosition Kafka!", min_length=1)


class GreetingResponse(BaseModel):
    topic: str
    key: str
    message: str
    status: str
