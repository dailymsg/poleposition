from typing import Any

from {{package_name}}.integrations.rabbitmq.publisher import RabbitMQEventPublisher
from {{package_name}}.settings import get_settings


def build_rabbitmq_event_publisher() -> RabbitMQEventPublisher:
    settings = get_settings()

    try:
        from aio_pika import connect_robust
    except ImportError as exc:
        raise RuntimeError(
            "RabbitMQ integration requires aio-pika. Run `uv sync --extra dev` after "
            "`polepos add integration rabbitmq`."
        ) from exc

    async def connect():
        return await connect_robust(
            settings.rabbitmq_url,
            client_properties={"connection_name": settings.rabbitmq_client_id},
        )

    return RabbitMQEventPublisher(
        connect,
        exchange_name=settings.rabbitmq_exchange,
        exchange_type=settings.rabbitmq_exchange_type,
        exchange_durable=settings.rabbitmq_exchange_durable,
    )


async def build_rabbitmq_queue(
    *,
    queue_name: str | None = None,
    routing_key: str | None = None,
) -> tuple[Any, Any]:
    settings = get_settings()

    try:
        from aio_pika import connect_robust
    except ImportError as exc:
        raise RuntimeError(
            "RabbitMQ integration requires aio-pika. Run `uv sync --extra dev` after "
            "`polepos add integration rabbitmq`."
        ) from exc

    connection = await connect_robust(
        settings.rabbitmq_url,
        client_properties={"connection_name": settings.rabbitmq_client_id},
    )
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=settings.rabbitmq_prefetch_count)
    exchange = await channel.declare_exchange(
        settings.rabbitmq_exchange,
        settings.rabbitmq_exchange_type,
        durable=settings.rabbitmq_exchange_durable,
    )
    queue = await channel.declare_queue(
        queue_name or settings.rabbitmq_default_queue,
        durable=settings.rabbitmq_queue_durable,
    )
    await queue.bind(
        exchange,
        routing_key or settings.rabbitmq_default_routing_key,
    )
    return connection, queue
