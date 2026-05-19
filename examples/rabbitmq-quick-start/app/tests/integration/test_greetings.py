from fastapi.testclient import TestClient

from rabbitmq_quick_start.integrations.rabbitmq.testing import (
    InMemoryRabbitMQEventPublisher,
)
from rabbitmq_quick_start.modules.greetings import router as greetings_router


def test_send_greeting_publishes_message(client: TestClient, monkeypatch) -> None:
    publisher = InMemoryRabbitMQEventPublisher()
    monkeypatch.setattr(
        greetings_router,
        "build_rabbitmq_event_publisher",
        lambda: publisher,
    )

    response = client.post(
        "/api/v1/greetings/send",
        json={
            "recipient": "team",
            "message": "Hello, PolePosition RabbitMQ!",
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "routing_key": "greetings.created",
        "message": "Hello, PolePosition RabbitMQ!",
        "status": "published",
    }
    assert len(publisher.messages) == 1
    assert publisher.messages[0].routing_key == "greetings.created"
    assert publisher.messages[0].value == {
        "recipient": "team",
        "message": "Hello, PolePosition RabbitMQ!",
    }
