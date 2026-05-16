# Kafka Integration

Add Kafka helpers to an existing PolePosition project:

```bash
polepos add integration kafka
```

The command creates:

```text
src/<package>/integrations/kafka/
  __init__.py
  consumer.py
  factory.py
  producer.py
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
aiokafka>=0.12.0
```

Sync dependencies after adding the integration:

```bash
uv sync
```

## Settings

Review the Kafka values in `.env`:

```env
KAFKA_ENABLED=false
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_CLIENT_ID=<package>
KAFKA_DEFAULT_TOPIC=<package>.events
KAFKA_GROUP_ID=<package>
KAFKA_AUTO_OFFSET_RESET=earliest
KAFKA_ACKS=all
# KAFKA_COMPRESSION_TYPE=
KAFKA_REQUEST_TIMEOUT_MS=40000
```

Required Kafka values should remain active in `.env.example`. A commented
required value such as `# KAFKA_BOOTSTRAP_SERVERS=localhost:9092` is treated as
missing by `polepos check`. `KAFKA_COMPRESSION_TYPE` is optional and may remain
commented until needed.

## Use the Producer

The generated factory builds a producer from settings. Keep producer lifetime
management explicit in your route, service, or application wiring.

Use the generated schemas to keep event payloads predictable.

## Consumers and Workers

The generated consumer helper is scaffolding for a worker surface. It is not
started automatically by the FastAPI app.

For production, run consumers as explicit worker processes or jobs so API
startup remains fast and predictable.

## Testing

Use `InMemoryKafkaEventProducer` from `testing.py` when unit tests should assert
published events without connecting to Kafka.

## Validate

```bash
polepos check
```

The check command validates Kafka files, settings, env values, and dependency
signals without connecting to Kafka. It distinguishes required active env keys
from optional commented examples.
