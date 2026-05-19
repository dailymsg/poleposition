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
