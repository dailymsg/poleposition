# RabbitMQ Quick Start Scenario

This guide uses the same first-message shape as the Kafka tutorial, but maps it
to RabbitMQ.

RabbitMQ is a better first choice than Kafka when the workflow is a queue or
work-dispatch problem: publish a message, let one or more workers handle it, and
acknowledge each message when processing succeeds.

The PolePosition version uses:

- `polepos add integration rabbitmq` for publisher, queue factory, consumer
  helper, schemas, settings, env values, and test double
- `polepos add module greetings --api-only` for the HTTP boundary
- a module-local worker for message consumption

## Complete Runnable Source

This example includes a complete PolePosition-generated project:

```text
examples/rabbitmq-quick-start/app/
```

Run it directly:

```bash
cd examples/rabbitmq-quick-start/app
cp .env.example .env
uv sync --extra dev
docker compose -f compose.rabbitmq.yaml up -d
uv run python -m rabbitmq_quick_start.run
```

The rest of this guide explains how that `app/` project was built and why each
file exists.

## Scenario Goal

Build a small queue-backed API:

```text
POST /api/v1/greetings/send
```

The endpoint publishes a JSON message to a RabbitMQ exchange with routing key
`greetings.created`:

```json
{
  "recipient": "team",
  "message": "Hello, PolePosition RabbitMQ!"
}
```

A worker consumes the queue and prints:

```text
got: Hello, PolePosition RabbitMQ!
```

## Step 1: Create the Project

This example does not need a database:

```bash
polepos start rabbitmq-quick-start --db none
cd rabbitmq-quick-start
cp .env.example .env
uv sync --extra dev
```

## Step 2: Add RabbitMQ

```bash
polepos add integration rabbitmq
uv sync --extra dev
```

PolePosition creates:

```text
src/rabbitmq_quick_start/integrations/rabbitmq/
  __init__.py
  consumer.py
  factory.py
  publisher.py
  schemas.py
  testing.py
```

Use these `.env` values:

```env
RABBITMQ_ENABLED=true
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_CLIENT_ID=rabbitmq_quick_start
RABBITMQ_EXCHANGE=greetings.events
RABBITMQ_EXCHANGE_TYPE=topic
RABBITMQ_EXCHANGE_DURABLE=true
RABBITMQ_DEFAULT_ROUTING_KEY=greetings.created
RABBITMQ_DEFAULT_QUEUE=greetings.demo
RABBITMQ_QUEUE_DURABLE=true
RABBITMQ_PREFETCH_COUNT=10
```

Why these settings matter:

- the exchange is the publishing target
- the routing key describes the kind of event
- the queue is what the worker consumes
- `prefetch_count` limits how many unacknowledged messages one worker receives

## Step 3: Run RabbitMQ Locally

Create `compose.rabbitmq.yaml`:

```yaml
services:
  rabbitmq:
    image: rabbitmq:3.13-management
    ports:
      - "5672:5672"
      - "15672:15672"
```

Start RabbitMQ:

```bash
docker compose -f compose.rabbitmq.yaml up -d
```

The management UI is available at:

```text
http://localhost:15672
```

Use username `guest` and password `guest`.

## Step 4: Generate the Greetings Module

```bash
polepos add module greetings --api-only
```

PolePosition creates:

```text
src/rabbitmq_quick_start/modules/greetings/
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

Replace `src/rabbitmq_quick_start/modules/greetings/schemas.py`:

```python
from pydantic import BaseModel, Field


class GreetingRequest(BaseModel):
    recipient: str = Field(default="team", min_length=1)
    message: str = Field(default="Hello, PolePosition RabbitMQ!", min_length=1)


class GreetingResponse(BaseModel):
    routing_key: str
    message: str
    status: str
```

Why this file exists:

- Pydantic validates incoming JSON before the service sees it
- the router can return a stable response shape to clients
- the routing key stays visible in the response for local debugging

## Step 6: Publish a Greeting Message

Replace
`src/rabbitmq_quick_start/modules/greetings/services/greetings_service.py`:

```python
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
```

What this service does:

- it builds the generated `RabbitMQMessage` shape
- it depends on a `Protocol` so tests can pass the generated in-memory publisher
- it keeps queue-specific encoding out of the module

Replace `src/rabbitmq_quick_start/modules/greetings/router.py`:

```python
from fastapi import APIRouter, status

from rabbitmq_quick_start.integrations.rabbitmq.factory import (
    build_rabbitmq_event_publisher,
)
from rabbitmq_quick_start.modules.greetings.schemas import (
    GreetingRequest,
    GreetingResponse,
)
from rabbitmq_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)
from rabbitmq_quick_start.settings import get_settings


router = APIRouter()


@router.post(
    "/send",
    response_model=GreetingResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_greeting(payload: GreetingRequest) -> GreetingResponse:
    settings = get_settings()
    publisher = build_rabbitmq_event_publisher()

    await publisher.start()
    try:
        message = await publish_greeting(
            publisher,
            routing_key=settings.rabbitmq_default_routing_key,
            recipient=payload.recipient,
            message=payload.message,
        )
    finally:
        await publisher.stop()

    return GreetingResponse(
        routing_key=message.routing_key,
        message=payload.message,
        status="published",
    )
```

What this router does:

- it returns `202 Accepted` because the actual work happens later in a worker
- it reads the routing key from settings
- it starts and stops the publisher explicitly for a clear tutorial

For production, move publisher lifetime into application lifespan wiring so
requests reuse a long-lived connection.

## Step 7: Add a Consumer Worker

Create `src/rabbitmq_quick_start/modules/greetings/consumer.py`:

```python
import asyncio
from typing import Any

from rabbitmq_quick_start.integrations.rabbitmq.consumer import consume_json_messages
from rabbitmq_quick_start.integrations.rabbitmq.factory import build_rabbitmq_queue


async def handle_greeting(payload: dict[str, Any], routing_key: str) -> None:
    print(f"got: {payload['message']}")


async def main() -> None:
    connection, queue = await build_rabbitmq_queue()
    try:
        await consume_json_messages(queue, handle_greeting)
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
```

Why this is a separate worker:

- RabbitMQ consumption is long-running background work
- message acknowledgements should be controlled by the worker
- API and worker processes can scale independently

Run FastAPI:

```bash
uv run python -m rabbitmq_quick_start.run
```

Run the worker:

```bash
uv run python -m rabbitmq_quick_start.modules.greetings.consumer
```

Publish a message:

```bash
curl -X POST http://localhost:8000/api/v1/greetings/send \
  -H "Content-Type: application/json" \
  -d '{"recipient":"team","message":"Hello, PolePosition RabbitMQ!"}'
```

Expected worker output:

```text
got: Hello, PolePosition RabbitMQ!
```

## Step 8: Test Without RabbitMQ

Replace `tests/unit/test_greetings_api_service.py`:

```python
import pytest

from rabbitmq_quick_start.integrations.rabbitmq.testing import (
    InMemoryRabbitMQEventPublisher,
)
from rabbitmq_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)


@pytest.mark.asyncio
async def test_publish_greeting_records_message() -> None:
    publisher = InMemoryRabbitMQEventPublisher()

    message = await publish_greeting(
        publisher,
        routing_key="greetings.created",
        recipient="team",
        message="hello from the test",
    )

    assert message.routing_key == "greetings.created"
    assert message.value == {
        "recipient": "team",
        "message": "hello from the test",
    }
    assert publisher.messages == [message]
```

Why this test is useful:

- it checks that module code creates the correct message
- it does not need Docker, ports, or a running broker
- it keeps real broker behavior for a separate integration suite

Run:

```bash
uv run pytest
polepos check
```

## RabbitMQ Versus Kafka In This Tutorial

| Concern | Kafka quick start | RabbitMQ quick start |
| --- | --- | --- |
| Primary abstraction | topic log | exchange plus queue |
| Delivery model | consumers read offsets | messages are acknowledged |
| Good first use case | event stream/history | job dispatch/work queue |
| Generated send helper | `KafkaEventProducer` | `RabbitMQEventPublisher` |
| Generated test double | `InMemoryKafkaEventProducer` | `InMemoryRabbitMQEventPublisher` |

Use RabbitMQ here when "do this work" is the dominant idea. Use Kafka when "this
event happened and multiple consumers may care now or later" is the dominant
idea.
