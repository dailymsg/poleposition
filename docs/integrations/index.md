# Integration Guides

PolePosition keeps external-system scaffolds opt-in. A new project starts lean,
then you add integration helpers only when the application needs them.

Current integration surfaces:

- [Kafka](kafka.md): event streaming producer, consumer helper, settings, env,
  dependency, and test double.
- [RabbitMQ](rabbitmq.md): AMQP publisher, consumer helper, queue factory,
  settings, env, dependency, and test double.
- [LLM](llm.md): provider-agnostic adapter stubs generated with an AI prompt
  module.

Integration scaffolds are starting points. They do not start background
consumer loops inside the FastAPI application process. Keep long-running
workers explicit in your deployment or runtime code.

After adding an integration, run:

```bash
polepos check
uv sync
```

