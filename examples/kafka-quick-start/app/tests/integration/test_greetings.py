from fastapi.testclient import TestClient

from kafka_quick_start.integrations.kafka.testing import InMemoryKafkaEventProducer
from kafka_quick_start.modules.greetings import router as greetings_router


def test_send_greeting_publishes_event(client: TestClient, monkeypatch) -> None:
    producer = InMemoryKafkaEventProducer()
    monkeypatch.setattr(
        greetings_router,
        "build_kafka_event_producer",
        lambda: producer,
    )

    response = client.post(
        "/api/v1/greetings/send",
        json={
            "recipient": "team",
            "message": "Hello, PolePosition Kafka!",
        },
    )

    assert response.status_code == 202
    assert response.json() == {
        "topic": "greetings",
        "key": "team",
        "message": "Hello, PolePosition Kafka!",
        "status": "published",
    }
    assert len(producer.events) == 1
    assert producer.events[0].topic == "greetings"
    assert producer.events[0].key == "team"
    assert producer.events[0].value == {
        "recipient": "team",
        "message": "Hello, PolePosition Kafka!",
    }
