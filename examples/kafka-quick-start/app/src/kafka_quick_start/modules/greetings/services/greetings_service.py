from typing import Protocol

from kafka_quick_start.integrations.kafka.schemas import KafkaEvent


class GreetingEventProducer(Protocol):
    async def publish(self, event: KafkaEvent) -> None:
        ...


async def publish_greeting(
    producer: GreetingEventProducer,
    *,
    topic: str,
    recipient: str,
    message: str,
) -> KafkaEvent:
    event = KafkaEvent(
        topic=topic,
        key=recipient,
        value={
            "recipient": recipient,
            "message": message,
        },
    )
    await producer.publish(event)
    return event
