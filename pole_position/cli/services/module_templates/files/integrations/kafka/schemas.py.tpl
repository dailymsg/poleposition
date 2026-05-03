import json
from typing import Any

from pydantic import BaseModel, Field


class KafkaEvent(BaseModel):
    topic: str
    value: dict[str, Any]
    key: str | None = None
    headers: dict[str, str] = Field(default_factory=dict)


def encode_event_value(event: KafkaEvent) -> bytes:
    return json.dumps(
        event.value,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def encode_event_key(event: KafkaEvent) -> bytes | None:
    if event.key is None:
        return None

    return event.key.encode("utf-8")


def encode_event_headers(event: KafkaEvent) -> list[tuple[str, bytes]] | None:
    if not event.headers:
        return None

    return [
        (name, value.encode("utf-8"))
        for name, value in sorted(event.headers.items())
    ]


def decode_event_value(value: bytes) -> dict[str, Any]:
    return json.loads(value.decode("utf-8"))
