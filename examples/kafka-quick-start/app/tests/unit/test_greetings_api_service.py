import asyncio

from kafka_quick_start.integrations.kafka.testing import InMemoryKafkaEventProducer
from kafka_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)


def test_publish_greeting_records_event() -> None:
    producer = InMemoryKafkaEventProducer()

    event = asyncio.run(
        publish_greeting(
            producer,
            topic="greetings",
            recipient="team",
            message="hello from the test",
        )
    )

    assert event.topic == "greetings"
    assert event.key == "team"
    assert event.value == {
        "recipient": "team",
        "message": "hello from the test",
    }
    assert producer.events == [event]
