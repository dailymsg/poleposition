from collections.abc import Awaitable, Callable
from typing import Any, Protocol

from rabbitmq_quick_start.bootstrap.logging import get_logger
from rabbitmq_quick_start.integrations.rabbitmq.schemas import decode_message_value


logger = get_logger(__name__)


class RabbitMQIncomingMessage(Protocol):
    body: bytes
    routing_key: str

    def process(self):
        ...


class RabbitMQQueue(Protocol):
    def iterator(self):
        ...


MessageHandler = Callable[[dict[str, Any], str], Awaitable[None]]


async def consume_json_messages(
    queue: RabbitMQQueue,
    handler: MessageHandler,
) -> None:
    async with queue.iterator() as queue_iterator:
        async for message in queue_iterator:
            async with message.process():
                payload = decode_message_value(message.body)
                await handler(payload, message.routing_key)
                logger.info(
                    "Consumed RabbitMQ message",
                    extra={"routing_key": message.routing_key},
                )
