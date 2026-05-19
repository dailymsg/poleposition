from typing import Protocol

from rabbitmq_quick_start.integrations.rabbitmq.schemas import RabbitMQMessage


class GreetingMessagePublisher(Protocol):
    async def publish(self, message: RabbitMQMessage) -> None:
        ...


async def publish_greeting(
    publisher: GreetingMessagePublisher,
    *,
    routing_key: str,
    recipient: str,
    message: str,
) -> RabbitMQMessage:
    outbound = RabbitMQMessage(
        routing_key=routing_key,
        value={
            "recipient": recipient,
            "message": message,
        },
    )
    await publisher.publish(outbound)
    return outbound
