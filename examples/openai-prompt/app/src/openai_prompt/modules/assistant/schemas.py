from pydantic import BaseModel, Field


class AssistantPromptRequest(BaseModel):
    prompt: str = Field(min_length=1)
    topic: str = Field(default="general", min_length=1, max_length=100)


class AssistantPromptResponse(BaseModel):
    response: str
    provider: str
    model: str
    topic: str
