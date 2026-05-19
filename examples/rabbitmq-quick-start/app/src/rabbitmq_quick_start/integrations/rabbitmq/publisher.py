from collections.abc import Awaitable, Callable
from typing import Protocol

from rabbitmq_quick_start.bootstrap.logging import get_logger
from rabbitmq_quick_start.integrations.rabbitmq.schemas import (
    RabbitMQMessage,
    encode_message_value,
)


logger = get_logger(__name__)


class RabbitMQExchange(Protocol):
    async def publish(self, message: object, routing_key: str) -> object:
        ...


class RabbitMQChannel(Protocol):
    async def declare_exchange(
        self,
        name: str,
        type: str,
        *,
        durable: bool,
    ) -> RabbitMQExchange:
        ...


class RabbitMQConnection(Protocol):
    async def channel(self) -> RabbitMQChannel:
        ...

    async def close(self) -> None:
        ...


RabbitMQConnector = Callable[[], Awaitable[RabbitMQConnection]]


class RabbitMQEventPublisher:
    def __init__(
        self,
        connector: RabbitMQConnector,
        *,
        exchange_name: str,
        exchange_type: str,
        exchange_durable: bool,
    ) -> None:
        self.connector = connector
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.exchange_durable = exchange_durable
        self.connection: RabbitMQConnection | None = None
        self.exchange: RabbitMQExchange | None = None

    async def start(self) -> None:
        self.connection = await self.connector()
        channel = await self.connection.channel()
        self.exchange = await channel.declare_exchange(
            self.exchange_name,
            self.exchange_type,
            durable=self.exchange_durable,
        )

    async def stop(self) -> None:
        if self.connection is not None:
            await self.connection.close()
        self.connection = None
        self.exchange = None

    async def publish(self, message: RabbitMQMessage) -> None:
        if self.exchange is None:
            raise RuntimeError("RabbitMQ publisher has not been started.")

        try:
            from aio_pika import DeliveryMode, Message
        except ImportError as exc:
            raise RuntimeError(
                "RabbitMQ integration requires aio-pika. Run `uv sync --extra dev` after "
                "`polepos add integration rabbitmq`."
            ) from exc

        await self.exchange.publish(
            Message(
                encode_message_value(message),
                content_type="application/json",
                delivery_mode=DeliveryMode.PERSISTENT,
                headers=message.headers or None,
            ),
            message.routing_key,
        )
        logger.info(
            "Published RabbitMQ message",
            extra={
                "routing_key": message.routing_key,
                "exchange": self.exchange_name,
            },
        )
