# Examples

This directory contains concrete usage scenarios for PolePosition.

These examples are useful when you want to understand not only what the CLI generates, but how a generated project should be adapted for a real use case.

## Available Examples

### Auth Foundation

Path:

```text
examples/auth-foundation/README.md
```

Focus:

- public versus protected endpoints
- JWT-based current user resolution
- role-gated route example
- local token generation for testing

Use this when you want to understand how the generated auth layer is supposed to be used before a full login system exists.

### HTML Swap

Path:

```text
examples/html-swap/README.md
```

Focus:

- `polepos add module html --api-only`
- reshaping a generated module into a transformation-focused endpoint
- PostgreSQL-backed swap history
- `POST /api/v1/html/swap`

Use this when you want to see how a non-generic business use case can still fit the PolePosition structure.

### Kafka Quick Start

Path:

```text
examples/kafka-quick-start/README.md
```

Focus:

- adapting a Spring Kafka quick-start shape to PolePosition
- complete runnable source under `examples/kafka-quick-start/app`
- `polepos add integration kafka`
- `polepos add module greetings --api-only`
- publishing a JSON greeting event through FastAPI
- consuming the event from a module-local worker

Use this when you want a first Kafka producer/consumer example without turning
the generated FastAPI app into a background-worker host.

### RabbitMQ Quick Start

Path:

```text
examples/rabbitmq-quick-start/README.md
```

Focus:

- complete runnable source under `examples/rabbitmq-quick-start/app`
- `polepos add integration rabbitmq`
- queue-backed async work with exchange, routing key, and queue
- `polepos add module greetings --api-only`
- publishing a greeting message through FastAPI
- consuming the message from a module-local worker

Use this when the workflow is closer to job dispatch or work queues than event
streaming.

### Redis Cache

Path:

```text
examples/redis-cache/README.md
```

Focus:

- complete runnable source under `examples/redis-cache/app`
- `polepos add integration redis`
- cache-aside flow with `get_text` and `set_text`
- `polepos add module quotes --api-only`
- TTL-backed cached responses
- in-memory cache tests without Redis

Use this when you want a practical shared cache example that keeps Redis behind
module service code.

### OpenAI Prompt

Path:

```text
examples/openai-prompt/README.md
```

Focus:

- complete runnable source under `examples/openai-prompt/app`
- `polepos add module assistant --template ai-prompt`
- implementing the generated OpenAI provider adapter
- sending prompts with the OpenAI Responses API
- keeping live provider calls out of default unit tests

Use this when you want to turn the provider-agnostic AI scaffold into a working
OpenAI-backed endpoint.

## Why These Examples Matter

The template shows the default generated state.
The examples show the next step:

- what to keep
- what to rewrite
- what the real endpoint contract should look like
- how the generated project supports the use case

That makes examples especially useful for:

- onboarding
- architecture review
- agent understanding
- product direction discussions
