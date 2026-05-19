# Kafka Quick Start Scenario

This guide adapts the ideas from
[Dan Vega's Spring Kafka quick start](https://github.com/danvega/spring-kafka-quick-start)
to a PolePosition-generated FastAPI project.

The Spring version demonstrates a minimal application that:

1. starts a local Kafka broker
2. creates a `greetings` topic
3. sends one greeting message
4. consumes the message with a listener
5. keeps the first test focused on send/receive behavior

The PolePosition version keeps the same learning goal, but maps it to the
generated project structure:

- `polepos add integration kafka` creates the Kafka producer, consumer factory,
  schemas, settings, env values, and test double
- `polepos add module greetings --api-only` creates the API boundary
- a module-local worker consumes messages explicitly instead of starting a
  consumer inside the FastAPI request process

## Scenario Goal

Build a tiny event-driven API:

```text
POST /api/v1/greetings/send
```

The endpoint publishes a JSON event to Kafka:

```json
{
  "recipient": "team",
  "message": "Hello, PolePosition Kafka!"
}
```

A separate worker consumes events from the same topic and prints:

```text
got: Hello, PolePosition Kafka!
```

This mirrors the Spring quick start's `KafkaTemplate` producer and
`@KafkaListener` consumer, but keeps API serving and consumer work as separate
runtime concerns.

## Step 1: Create the Project

Kafka is the point of this example, so start without database wiring:

```bash
polepos start kafka-quick-start --db none
cd kafka-quick-start
cp .env.example .env
uv sync --extra dev
```

## Step 2: Add Kafka

```bash
polepos add integration kafka
uv sync --extra dev
```

PolePosition creates:

```text
src/kafka_quick_start/integrations/kafka/
  __init__.py
  consumer.py
  factory.py
  producer.py
  schemas.py
  testing.py
```

It also updates `settings.py`, `.env.example`, `pyproject.toml`, and
`.poleposition.toml`.

Update `.env` for this scenario:

```env
KAFKA_ENABLED=true
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CLIENT_ID=kafka_quick_start
KAFKA_DEFAULT_TOPIC=greetings
KAFKA_GROUP_ID=greetings-demo
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_ACKS=all
KAFKA_REQUEST_TIMEOUT_MS=40000
```

`KAFKA_AUTO_OFFSET_RESET=earliest` matches the important behavior in the Spring
quick start: a fresh consumer group should read messages that were sent before
the consumer joined.

## Step 3: Run Kafka Locally

Create `compose.kafka.yaml` in the generated project:

```yaml
services:
  kafka:
    image: apache/kafka:3.8.0
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://:29092,CONTROLLER://:9093,PLAINTEXT_HOST://:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@localhost:9093
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      CLUSTER_ID: "4L6g3nShT-eMCtK--X86sw"

  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    ports:
      - "8081:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
    depends_on:
      - kafka
```

Start Kafka:

```bash
docker compose -f compose.kafka.yaml up -d
```

Create the topic explicitly:

```bash
docker compose -f compose.kafka.yaml exec kafka \
  /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server kafka:29092 \
  --create \
  --if-not-exists \
  --topic greetings \
  --partitions 1 \
  --replication-factor 1
```

Kafka UI is available at:

```text
http://localhost:8081
```

## Step 4: Generate the Greetings Module

```bash
polepos add module greetings --api-only
```

PolePosition creates:

```text
src/kafka_quick_start/modules/greetings/
  __init__.py
  router.py
  schemas.py
  services/
    __init__.py
    greetings_service.py
tests/integration/test_greetings.py
tests/unit/test_greetings_api_service.py
```

## Step 5: Define the API Schema

Replace `src/kafka_quick_start/modules/greetings/schemas.py`:

```python
from pydantic import BaseModel, Field


class GreetingRequest(BaseModel):
    recipient: str = Field(default="team", min_length=1)
    message: str = Field(default="Hello, PolePosition Kafka!", min_length=1)


class GreetingResponse(BaseModel):
    topic: str
    key: str
    message: str
    status: str
```

Why this file exists:

- request and response models keep FastAPI validation at the edge of the module
- the router should not parse arbitrary dictionaries by hand
- `recipient` becomes the Kafka key so all events for the same recipient can be
  ordered together when the topic has multiple partitions later
- the response confirms publication intent, not downstream consumption

## Step 6: Publish a Greeting Event

Replace
`src/kafka_quick_start/modules/greetings/services/greetings_service.py`:

```python
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
```

What this service does:

- it accepts a producer through a small `Protocol`, so unit tests can pass an
  in-memory producer instead of a real Kafka client
- it builds one `KafkaEvent`, the generated integration's transport-neutral
  message shape
- it keeps use-case naming in the module (`publish_greeting`) and transport
  encoding in `integrations/kafka`

Replace `src/kafka_quick_start/modules/greetings/router.py`:

```python
from fastapi import APIRouter, status

from kafka_quick_start.integrations.kafka.factory import build_kafka_event_producer
from kafka_quick_start.modules.greetings.schemas import (
    GreetingRequest,
    GreetingResponse,
)
from kafka_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)
from kafka_quick_start.settings import get_settings


router = APIRouter()


@router.post(
    "/send",
    response_model=GreetingResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_greeting(payload: GreetingRequest) -> GreetingResponse:
    settings = get_settings()
    producer = build_kafka_event_producer()

    await producer.start()
    try:
        event = await publish_greeting(
            producer,
            topic=settings.kafka_default_topic,
            recipient=payload.recipient,
            message=payload.message,
        )
    finally:
        await producer.stop()

    return GreetingResponse(
        topic=event.topic,
        key=event.key or "",
        message=payload.message,
        status="published",
    )
```

What this router does:

- it owns the HTTP contract and returns `202 Accepted` because publishing an
  event queues work for later consumption
- it reads the topic from settings instead of hardcoding infrastructure details
  in the route
- it starts and stops the generated producer explicitly so the tutorial is easy
  to follow

For production traffic, move producer startup and shutdown into application
lifespan wiring so requests do not create a producer per call. The route should
then receive or resolve a long-lived producer instead.

## Step 7: Add a Consumer Worker

Create `src/kafka_quick_start/modules/greetings/consumer.py`:

```python
import asyncio
from typing import Any

from kafka_quick_start.integrations.kafka.consumer import consume_json_messages
from kafka_quick_start.integrations.kafka.factory import build_kafka_consumer
from kafka_quick_start.settings import get_settings


async def handle_greeting(
    topic: str,
    payload: dict[str, Any],
    key: str | None,
) -> None:
    print(f"got: {payload['message']}")


async def main() -> None:
    settings = get_settings()
    consumer = build_kafka_consumer(settings.kafka_default_topic)
    await consume_json_messages(consumer, handle_greeting)


if __name__ == "__main__":
    asyncio.run(main())
```

Why this is a separate module:

- a Kafka consumer is a worker process, not part of serving an HTTP request
- a crashing worker should not take down the FastAPI app process
- deployers can scale API instances and consumer instances independently
- the module still owns the business behavior for greetings, while the generic
  polling loop remains in `integrations/kafka`

Run FastAPI in one terminal:

```bash
uv run python -m kafka_quick_start.run
```

Run the consumer in another terminal:

```bash
uv run python -m kafka_quick_start.modules.greetings.consumer
```

Publish a message:

```bash
curl -X POST http://localhost:8000/api/v1/greetings/send \
  -H "Content-Type: application/json" \
  -d '{"recipient":"team","message":"Hello, PolePosition Kafka!"}'
```

The worker should print:

```text
got: Hello, PolePosition Kafka!
```

## Step 8: Test Without a Broker

Keep the unit test broker-free by using the generated in-memory producer.

Replace `tests/unit/test_greetings_api_service.py`:

```python
import pytest

from kafka_quick_start.integrations.kafka.testing import InMemoryKafkaEventProducer
from kafka_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)


@pytest.mark.asyncio
async def test_publish_greeting_records_event() -> None:
    producer = InMemoryKafkaEventProducer()

    event = await publish_greeting(
        producer,
        topic="greetings",
        recipient="team",
        message="hello from the test",
    )

    assert event.topic == "greetings"
    assert event.key == "team"
    assert event.value == {
        "recipient": "team",
        "message": "hello from the test",
    }
    assert producer.events == [event]
```

Why this test does not start Kafka:

- it tests the business contract: a greeting request becomes the expected event
- it stays fast enough for the default `uv run pytest` loop
- broker lifecycle, ports, and Docker availability are left to a separate
  integration test suite

Run:

```bash
uv run pytest
polepos check
```

For a real broker integration test, use a dedicated Docker/Testcontainers flow
and keep it separate from the fast default unit suite.

## Mapping From Spring to PolePosition

| Spring quick start | PolePosition equivalent |
| --- | --- |
| `KafkaTemplate` | generated `KafkaEventProducer` |
| `@KafkaListener` | module-local worker using `consume_json_messages` |
| `NewTopic` bean | explicit topic creation command or reviewed infra migration |
| `application.yaml` Kafka settings | `.env` plus generated `settings.py` fields |
| `EmbeddedKafka` test | broker-free unit test with `InMemoryKafkaEventProducer`; optional separate broker integration test |
| Spring Boot Docker Compose support | explicit `docker compose -f compose.kafka.yaml up -d` |

## Why This Shape

PolePosition keeps Kafka opt-in and explicit:

- API routes stay FastAPI-native
- Kafka producer/consumer code lives under `integrations/kafka`
- use-case behavior lives under `modules/greetings`
- consumers run as separate worker processes
- `polepos check` validates generated wiring without needing Kafka to be running

That keeps the first Kafka example small while preserving the production shape a
team would want later.
