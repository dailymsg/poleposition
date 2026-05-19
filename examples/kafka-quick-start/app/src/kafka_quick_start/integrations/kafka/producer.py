from typing import Protocol

from kafka_quick_start.bootstrap.logging import get_logger
from kafka_quick_start.integrations.kafka.schemas import (
    KafkaEvent,
    encode_event_headers,
    encode_event_key,
    encode_event_value,
)


logger = get_logger(__name__)


class KafkaProducerClient(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    async def send_and_wait(
        self,
        topic: str,
        value: bytes,
        *,
        key: bytes | None = None,
        headers: list[tuple[str, bytes]] | None = None,
    ) -> object:
        ...


class KafkaEventProducer:
    def __init__(self, client: KafkaProducerClient) -> None:
        self.client = client

    async def start(self) -> None:
        await self.client.start()

    async def stop(self) -> None:
        await self.client.stop()

    async def publish(self, event: KafkaEvent) -> None:
        await self.client.send_and_wait(
            event.topic,
            encode_event_value(event),
            key=encode_event_key(event),
            headers=encode_event_headers(event),
        )
        logger.info(
            "Published Kafka event",
            extra={
                "topic": event.topic,
                "event_key": event.key or "-",
            },
        )
