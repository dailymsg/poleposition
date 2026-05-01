from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    subject: str = Field(min_length=1)
    email: str | None = None
    roles: list[str] = Field(default_factory=list)
