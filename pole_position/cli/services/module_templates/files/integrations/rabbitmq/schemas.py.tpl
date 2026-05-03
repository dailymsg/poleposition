import json
from typing import Any

from pydantic import BaseModel, Field


class RabbitMQMessage(BaseModel):
    routing_key: str
    value: dict[str, Any]
    headers: dict[str, str] = Field(default_factory=dict)


def encode_message_value(message: RabbitMQMessage) -> bytes:
    return json.dumps(
        message.value,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def decode_message_value(value: bytes) -> dict[str, Any]:
    return json.loads(value.decode("utf-8"))
