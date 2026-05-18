from pydantic import BaseModel, Field


class RqJobInfo(BaseModel):
    id: str
    queue_name: str = Field(min_length=1)
    status: str
