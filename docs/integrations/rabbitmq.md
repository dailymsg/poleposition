# RabbitMQ Integration

Add RabbitMQ helpers to an existing PolePosition project:

```bash
polepos add integration rabbitmq
```

The command creates:

```text
src/<package>/integrations/rabbitmq/
  __init__.py
  consumer.py
  factory.py
  publisher.py
  schemas.py
  testing.py
```

It also updates:

- `src/<package>/settings.py`
- `.env.example`
- `pyproject.toml`

## Dependency

The command adds:

```text
aio-pika>=9.0.0
```

Sync dependencies after adding the integration:

```bash
uv sync --extra dev
```

## Settings

Review the RabbitMQ values in `.env`:

```env
RABBITMQ_ENABLED=false
RABBITMQ_URL=amqp://guest:guest@localhost:5672/
RABBITMQ_CLIENT_ID=<package>
RABBITMQ_EXCHANGE=<package>.events
RABBITMQ_EXCHANGE_TYPE=topic
RABBITMQ_EXCHANGE_DURABLE=true
RABBITMQ_DEFAULT_ROUTING_KEY=<package>.event
RABBITMQ_DEFAULT_QUEUE=<package>.events
RABBITMQ_QUEUE_DURABLE=true
RABBITMQ_PREFETCH_COUNT=10
```

RabbitMQ currently has no optional commented env examples. Required values in
`.env.example` should remain active so `polepos check` can validate the
integration contract.

## Use the Publisher

The generated factory builds a publisher from settings. Keep connection and
publisher lifetime management explicit in your runtime code.

Use the generated schemas to keep message payloads predictable.

For a complete first-message walkthrough, see the
[RabbitMQ Quick Start example](../examples/rabbitmq-quick-start.md).

## Consumers and Workers

The generated consumer helper is scaffolding for a worker surface. It is not
started automatically by the FastAPI app.

For production, run consumers as explicit worker processes or jobs so API
startup remains fast and predictable.

## Testing

Use `InMemoryRabbitMQEventPublisher` from `testing.py` when unit tests should
assert published messages without connecting to RabbitMQ.

## Validate

```bash
polepos check
```

The check command validates RabbitMQ files, settings, env values, and
dependency signals without connecting to RabbitMQ.
