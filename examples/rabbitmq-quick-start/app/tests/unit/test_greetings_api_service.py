import asyncio

from rabbitmq_quick_start.integrations.rabbitmq.testing import (
    InMemoryRabbitMQEventPublisher,
)
from rabbitmq_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)


def test_publish_greeting_records_message() -> None:
    publisher = InMemoryRabbitMQEventPublisher()

    message = asyncio.run(
        publish_greeting(
            publisher,
            routing_key="greetings.created",
            recipient="team",
            message="hello from the test",
        )
    )

    assert message.routing_key == "greetings.created"
    assert message.value == {
        "recipient": "team",
        "message": "hello from the test",
    }
    assert publisher.messages == [message]
