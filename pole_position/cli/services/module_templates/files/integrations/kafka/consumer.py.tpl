from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from {{package_name}}.bootstrap.logging import get_logger
from {{package_name}}.integrations.kafka.schemas import decode_event_value


logger = get_logger(__name__)


class KafkaMessage(Protocol):
    topic: str
    value: bytes
    key: bytes | None


class KafkaConsumerClient(Protocol):
    async def start(self) -> None:
        ...

    async def stop(self) -> None:
        ...

    def __aiter__(self):
        ...


EventHandler = Callable[[str, dict[str, Any], str | None], Awaitable[None]]


async def consume_json_messages(
    consumer: KafkaConsumerClient,
    handler: EventHandler,
) -> None:
    await consumer.start()
    try:
        async for message in consumer:
            key = message.key.decode("utf-8") if message.key else None
            payload = decode_event_value(message.value)
            await handler(message.topic, payload, key)
            logger.info(
                "Consumed Kafka event",
                extra={
                    "topic": message.topic,
                    "event_key": key or "-",
                },
            )
    finally:
        await consumer.stop()
