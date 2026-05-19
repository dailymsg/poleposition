# Integration Guides

PolePosition keeps external-system scaffolds opt-in. A new project starts lean,
then you add integration helpers only when the application needs them.

Current integration surfaces:

- [Kafka](kafka.md): event streaming producer, consumer helper, settings, env,
  dependency, and test double.
- [RabbitMQ](rabbitmq.md): AMQP publisher, consumer helper, queue factory,
  settings, env, dependency, and test double.
- [Redis](redis.md): async cache helper, settings, env, dependency, and test
  double.
- [RQ](rq.md): Redis-backed background job queue helpers, worker factory,
  settings, env, dependency, and test double.
- [LLM](llm.md): provider-agnostic adapter stubs generated with an AI prompt
  module.

Integration scaffolds are starting points. They do not start background
consumer loops inside the FastAPI application process. Keep long-running
workers explicit in your deployment or runtime code.

For end-to-end examples, see:

- [Kafka Quick Start](../examples/kafka-quick-start.md)
- [RabbitMQ Quick Start](../examples/rabbitmq-quick-start.md)
- [Redis Cache](../examples/redis-cache.md)
- [OpenAI Prompt](../examples/openai-prompt.md)

After adding an integration, run:

```bash
polepos check
uv sync --extra dev
```
