from pydantic import BaseModel, ConfigDict, Field


class TokenPayload(BaseModel):
    sub: str = Field(min_length=1)
    email: str | None = None
    roles: list[str] = Field(default_factory=list)


class AuthenticatedUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    subject: str
    email: str | None = None
    roles: list[str] = Field(default_factory=list)
