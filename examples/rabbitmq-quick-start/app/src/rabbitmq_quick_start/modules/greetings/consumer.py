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
