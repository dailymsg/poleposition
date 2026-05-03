from pathlib import Path
from textwrap import dedent

from pole_position.cli.services.integration_specs import (
    IntegrationContract,
    KAFKA_INTEGRATION_CONTRACT,
    RABBITMQ_INTEGRATION_CONTRACT,
    SUPPORTED_INTEGRATIONS,
    get_creatable_integration_contract,
)
from pole_position.cli.services.project_locator import find_package_root, find_project_root


SETTINGS_INTEGRATION_MARKER = "    # polepos:integration-settings"
SETTINGS_LLM_MARKER = "    # polepos:llm-settings"
ENV_INTEGRATION_MARKER = "# polepos:integration-env"
ENV_LLM_MARKER = "# polepos:llm-env"


def add_integration(integration_name: str, cwd: Path | None = None) -> None:
    contract = get_creatable_integration_contract(integration_name)

    project_root = find_project_root(cwd)
    package_root = find_package_root(cwd)
    package_name = package_root.name
    integration_root = package_root / "integrations" / contract.name

    _validate_add_integration_preflight(
        project_root=project_root,
        package_root=package_root,
        integration_root=integration_root,
        integration_name=contract.name,
    )

    if contract.name == "kafka":
        _ensure_integration_files(
            package_root,
            _kafka_integration_files(package_name),
        )
        _ensure_kafka_settings(package_root / "settings.py", package_name)
        _ensure_kafka_env(project_root / ".env.example", package_name)
        _ensure_project_dependency(project_root / "pyproject.toml", contract.dependency)
        return

    if contract.name == "rabbitmq":
        _ensure_integration_files(
            package_root,
            _rabbitmq_integration_files(package_name),
        )
        _ensure_rabbitmq_settings(package_root / "settings.py", package_name)
        _ensure_rabbitmq_env(project_root / ".env.example", package_name)
        _ensure_project_dependency(project_root / "pyproject.toml", contract.dependency)
        return


def _validate_add_integration_preflight(
    *,
    project_root: Path,
    package_root: Path,
    integration_root: Path,
    integration_name: str,
) -> None:
    problems: list[str] = []

    if integration_root.exists():
        problems.append(f"Integration already exists: {integration_name}")

    for path in [
        project_root / "pyproject.toml",
        project_root / ".env.example",
        package_root / "settings.py",
    ]:
        if not path.is_file():
            problems.append(f"Required managed file is missing: {path}")

    if problems:
        formatted_problems = "\n".join(f"- {problem}" for problem in problems)
        raise RuntimeError(
            "Cannot add integration because the project layout is not ready:\n"
            f"{formatted_problems}"
        )


def _ensure_integration_files(package_root: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        path = package_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _files_for_contract(
    contract: IntegrationContract,
    files: dict[str, str],
) -> dict[str, str]:
    missing = set(contract.file_names) - set(files)
    extra = set(files) - set(contract.file_names)
    if missing or extra:
        raise RuntimeError(f"Integration file contract drifted: {contract.name}")

    return {file_name: files[file_name] for file_name in contract.file_names}


def _kafka_integration_files(package_name: str) -> dict[str, str]:
    files = {
        "integrations/__init__.py": "",
        "integrations/kafka/__init__.py": _render_kafka_init(package_name),
        "integrations/kafka/consumer.py": _render_kafka_consumer(package_name),
        "integrations/kafka/factory.py": _render_kafka_factory(package_name),
        "integrations/kafka/producer.py": _render_kafka_producer(package_name),
        "integrations/kafka/schemas.py": _render_kafka_schemas(),
        "integrations/kafka/testing.py": _render_kafka_testing(package_name),
    }
    return _files_for_contract(KAFKA_INTEGRATION_CONTRACT, files)


def _render_kafka_init(package_name: str) -> str:
    return dedent(
        f'''\
        from {package_name}.integrations.kafka.factory import (
            build_kafka_consumer,
            build_kafka_event_producer,
        )
        from {package_name}.integrations.kafka.producer import KafkaEventProducer
        from {package_name}.integrations.kafka.schemas import KafkaEvent
        from {package_name}.integrations.kafka.testing import InMemoryKafkaEventProducer


        __all__ = [
            "KafkaEvent",
            "KafkaEventProducer",
            "InMemoryKafkaEventProducer",
            "build_kafka_consumer",
            "build_kafka_event_producer",
        ]
        '''
    )


def _render_kafka_schemas() -> str:
    return dedent(
        '''\
        import json
        from typing import Any

        from pydantic import BaseModel, Field


        class KafkaEvent(BaseModel):
            topic: str
            value: dict[str, Any]
            key: str | None = None
            headers: dict[str, str] = Field(default_factory=dict)


        def encode_event_value(event: KafkaEvent) -> bytes:
            return json.dumps(
                event.value,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")


        def encode_event_key(event: KafkaEvent) -> bytes | None:
            if event.key is None:
                return None

            return event.key.encode("utf-8")


        def encode_event_headers(event: KafkaEvent) -> list[tuple[str, bytes]] | None:
            if not event.headers:
                return None

            return [
                (name, value.encode("utf-8"))
                for name, value in sorted(event.headers.items())
            ]


        def decode_event_value(value: bytes) -> dict[str, Any]:
            return json.loads(value.decode("utf-8"))
        '''
    )


def _render_kafka_producer(package_name: str) -> str:
    return dedent(
        f'''\
        from typing import Protocol

        from {package_name}.bootstrap.logging import get_logger
        from {package_name}.integrations.kafka.schemas import (
            KafkaEvent,
            encode_event_headers,
            encode_event_key,
            encode_event_value,
        )


        logger = get_logger(__name__)


        class KafkaProducerClient(Protocol):
            async def start(self) -> None:
                ...

            async def stop(self) -> None:
                ...

            async def send_and_wait(
                self,
                topic: str,
                value: bytes,
                *,
                key: bytes | None = None,
                headers: list[tuple[str, bytes]] | None = None,
            ) -> object:
                ...


        class KafkaEventProducer:
            def __init__(self, client: KafkaProducerClient) -> None:
                self.client = client

            async def start(self) -> None:
                await self.client.start()

            async def stop(self) -> None:
                await self.client.stop()

            async def publish(self, event: KafkaEvent) -> None:
                await self.client.send_and_wait(
                    event.topic,
                    encode_event_value(event),
                    key=encode_event_key(event),
                    headers=encode_event_headers(event),
                )
                logger.info(
                    "Published Kafka event",
                    extra={{
                        "topic": event.topic,
                        "event_key": event.key or "-",
                    }},
                )
        '''
    )


def _render_kafka_factory(package_name: str) -> str:
    return dedent(
        f'''\
        from {package_name}.integrations.kafka.producer import KafkaEventProducer
        from {package_name}.settings import get_settings


        def build_kafka_event_producer() -> KafkaEventProducer:
            settings = get_settings()

            try:
                from aiokafka import AIOKafkaProducer
            except ImportError as exc:
                raise RuntimeError(
                    "Kafka integration requires aiokafka. Run `uv sync` after "
                    "`polepos add integration kafka`."
                ) from exc

            return KafkaEventProducer(
                AIOKafkaProducer(
                    bootstrap_servers=settings.kafka_bootstrap_servers,
                    client_id=settings.kafka_client_id,
                    acks=settings.kafka_acks,
                    compression_type=settings.kafka_compression_type or None,
                    request_timeout_ms=settings.kafka_request_timeout_ms,
                )
            )


        def build_kafka_consumer(*topics: str):
            settings = get_settings()

            try:
                from aiokafka import AIOKafkaConsumer
            except ImportError as exc:
                raise RuntimeError(
                    "Kafka integration requires aiokafka. Run `uv sync` after "
                    "`polepos add integration kafka`."
                ) from exc

            return AIOKafkaConsumer(
                *topics,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                client_id=settings.kafka_client_id,
                group_id=settings.kafka_group_id,
                auto_offset_reset=settings.kafka_auto_offset_reset,
            )
        '''
    )


def _render_kafka_consumer(package_name: str) -> str:
    return dedent(
        f'''\
        from collections.abc import Awaitable, Callable
        from typing import Any, Protocol

        from {package_name}.bootstrap.logging import get_logger
        from {package_name}.integrations.kafka.schemas import decode_event_value


        logger = get_logger(__name__)


        class KafkaMessage(Protocol):
            topic: str
            value: bytes
            key: bytes | None


        class KafkaConsumerClient(Protocol):
            async def start(self) -> None:
                ...

            async def stop(self) -> None:
                ...

            def __aiter__(self):
                ...


        EventHandler = Callable[[str, dict[str, Any], str | None], Awaitable[None]]


        async def consume_json_messages(
            consumer: KafkaConsumerClient,
            handler: EventHandler,
        ) -> None:
            await consumer.start()
            try:
                async for message in consumer:
                    key = message.key.decode("utf-8") if message.key else None
                    payload = decode_event_value(message.value)
                    await handler(message.topic, payload, key)
                    logger.info(
                        "Consumed Kafka event",
                        extra={{
                            "topic": message.topic,
                            "event_key": key or "-",
                        }},
                    )
            finally:
                await consumer.stop()
        '''
    )


def _render_kafka_testing(package_name: str) -> str:
    return dedent(
        f'''\
        from {package_name}.integrations.kafka.schemas import KafkaEvent


        class InMemoryKafkaEventProducer:
            def __init__(self) -> None:
                self.events: list[KafkaEvent] = []
                self.started = False

            async def start(self) -> None:
                self.started = True

            async def stop(self) -> None:
                self.started = False

            async def publish(self, event: KafkaEvent) -> None:
                self.events.append(event)
        '''
    )


def _rabbitmq_integration_files(package_name: str) -> dict[str, str]:
    files = {
        "integrations/__init__.py": "",
        "integrations/rabbitmq/__init__.py": _render_rabbitmq_init(package_name),
        "integrations/rabbitmq/consumer.py": _render_rabbitmq_consumer(package_name),
        "integrations/rabbitmq/factory.py": _render_rabbitmq_factory(package_name),
        "integrations/rabbitmq/publisher.py": _render_rabbitmq_publisher(package_name),
        "integrations/rabbitmq/schemas.py": _render_rabbitmq_schemas(),
        "integrations/rabbitmq/testing.py": _render_rabbitmq_testing(package_name),
    }
    return _files_for_contract(RABBITMQ_INTEGRATION_CONTRACT, files)


def _render_rabbitmq_init(package_name: str) -> str:
    return dedent(
        f'''\
        from {package_name}.integrations.rabbitmq.factory import (
            build_rabbitmq_event_publisher,
            build_rabbitmq_queue,
        )
        from {package_name}.integrations.rabbitmq.publisher import RabbitMQEventPublisher
        from {package_name}.integrations.rabbitmq.schemas import RabbitMQMessage
        from {package_name}.integrations.rabbitmq.testing import InMemoryRabbitMQEventPublisher


        __all__ = [
            "RabbitMQMessage",
            "RabbitMQEventPublisher",
            "InMemoryRabbitMQEventPublisher",
            "build_rabbitmq_event_publisher",
            "build_rabbitmq_queue",
        ]
        '''
    )


def _render_rabbitmq_schemas() -> str:
    return dedent(
        '''\
        import json
        from typing import Any

        from pydantic import BaseModel, Field


        class RabbitMQMessage(BaseModel):
            routing_key: str
            value: dict[str, Any]
            headers: dict[str, str] = Field(default_factory=dict)


        def encode_message_value(message: RabbitMQMessage) -> bytes:
            return json.dumps(
                message.value,
                separators=(",", ":"),
                sort_keys=True,
            ).encode("utf-8")


        def decode_message_value(value: bytes) -> dict[str, Any]:
            return json.loads(value.decode("utf-8"))
        '''
    )


def _render_rabbitmq_publisher(package_name: str) -> str:
    return dedent(
        f'''\
        from collections.abc import Awaitable, Callable
        from typing import Protocol

        from {package_name}.bootstrap.logging import get_logger
        from {package_name}.integrations.rabbitmq.schemas import (
            RabbitMQMessage,
            encode_message_value,
        )


        logger = get_logger(__name__)


        class RabbitMQExchange(Protocol):
            async def publish(self, message: object, routing_key: str) -> object:
                ...


        class RabbitMQChannel(Protocol):
            async def declare_exchange(
                self,
                name: str,
                type: str,
                *,
                durable: bool,
            ) -> RabbitMQExchange:
                ...


        class RabbitMQConnection(Protocol):
            async def channel(self) -> RabbitMQChannel:
                ...

            async def close(self) -> None:
                ...


        RabbitMQConnector = Callable[[], Awaitable[RabbitMQConnection]]


        class RabbitMQEventPublisher:
            def __init__(
                self,
                connector: RabbitMQConnector,
                *,
                exchange_name: str,
                exchange_type: str,
                exchange_durable: bool,
            ) -> None:
                self.connector = connector
                self.exchange_name = exchange_name
                self.exchange_type = exchange_type
                self.exchange_durable = exchange_durable
                self.connection: RabbitMQConnection | None = None
                self.exchange: RabbitMQExchange | None = None

            async def start(self) -> None:
                self.connection = await self.connector()
                channel = await self.connection.channel()
                self.exchange = await channel.declare_exchange(
                    self.exchange_name,
                    self.exchange_type,
                    durable=self.exchange_durable,
                )

            async def stop(self) -> None:
                if self.connection is not None:
                    await self.connection.close()
                self.connection = None
                self.exchange = None

            async def publish(self, message: RabbitMQMessage) -> None:
                if self.exchange is None:
                    raise RuntimeError("RabbitMQ publisher has not been started.")

                try:
                    from aio_pika import DeliveryMode, Message
                except ImportError as exc:
                    raise RuntimeError(
                        "RabbitMQ integration requires aio-pika. Run `uv sync` after "
                        "`polepos add integration rabbitmq`."
                    ) from exc

                await self.exchange.publish(
                    Message(
                        encode_message_value(message),
                        content_type="application/json",
                        delivery_mode=DeliveryMode.PERSISTENT,
                        headers=message.headers or None,
                    ),
                    message.routing_key,
                )
                logger.info(
                    "Published RabbitMQ message",
                    extra={{
                        "routing_key": message.routing_key,
                        "exchange": self.exchange_name,
                    }},
                )
        '''
    )


def _render_rabbitmq_factory(package_name: str) -> str:
    return dedent(
        f'''\
        from typing import Any

        from {package_name}.integrations.rabbitmq.publisher import RabbitMQEventPublisher
        from {package_name}.settings import get_settings


        def build_rabbitmq_event_publisher() -> RabbitMQEventPublisher:
            settings = get_settings()

            try:
                from aio_pika import connect_robust
            except ImportError as exc:
                raise RuntimeError(
                    "RabbitMQ integration requires aio-pika. Run `uv sync` after "
                    "`polepos add integration rabbitmq`."
                ) from exc

            async def connect():
                return await connect_robust(
                    settings.rabbitmq_url,
                    client_properties={{"connection_name": settings.rabbitmq_client_id}},
                )

            return RabbitMQEventPublisher(
                connect,
                exchange_name=settings.rabbitmq_exchange,
                exchange_type=settings.rabbitmq_exchange_type,
                exchange_durable=settings.rabbitmq_exchange_durable,
            )


        async def build_rabbitmq_queue(
            *,
            queue_name: str | None = None,
            routing_key: str | None = None,
        ) -> tuple[Any, Any]:
            settings = get_settings()

            try:
                from aio_pika import connect_robust
            except ImportError as exc:
                raise RuntimeError(
                    "RabbitMQ integration requires aio-pika. Run `uv sync` after "
                    "`polepos add integration rabbitmq`."
                ) from exc

            connection = await connect_robust(
                settings.rabbitmq_url,
                client_properties={{"connection_name": settings.rabbitmq_client_id}},
            )
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=settings.rabbitmq_prefetch_count)
            exchange = await channel.declare_exchange(
                settings.rabbitmq_exchange,
                settings.rabbitmq_exchange_type,
                durable=settings.rabbitmq_exchange_durable,
            )
            queue = await channel.declare_queue(
                queue_name or settings.rabbitmq_default_queue,
                durable=settings.rabbitmq_queue_durable,
            )
            await queue.bind(
                exchange,
                routing_key or settings.rabbitmq_default_routing_key,
            )
            return connection, queue
        '''
    )


def _render_rabbitmq_consumer(package_name: str) -> str:
    return dedent(
        f'''\
        from collections.abc import Awaitable, Callable
        from typing import Any, Protocol

        from {package_name}.bootstrap.logging import get_logger
        from {package_name}.integrations.rabbitmq.schemas import decode_message_value


        logger = get_logger(__name__)


        class RabbitMQIncomingMessage(Protocol):
            body: bytes
            routing_key: str

            def process(self):
                ...


        class RabbitMQQueue(Protocol):
            def iterator(self):
                ...


        MessageHandler = Callable[[dict[str, Any], str], Awaitable[None]]


        async def consume_json_messages(
            queue: RabbitMQQueue,
            handler: MessageHandler,
        ) -> None:
            async with queue.iterator() as queue_iterator:
                async for message in queue_iterator:
                    async with message.process():
                        payload = decode_message_value(message.body)
                        await handler(payload, message.routing_key)
                        logger.info(
                            "Consumed RabbitMQ message",
                            extra={{"routing_key": message.routing_key}},
                        )
        '''
    )


def _render_rabbitmq_testing(package_name: str) -> str:
    return dedent(
        f'''\
        from {package_name}.integrations.rabbitmq.schemas import RabbitMQMessage


        class InMemoryRabbitMQEventPublisher:
            def __init__(self) -> None:
                self.messages: list[RabbitMQMessage] = []
                self.started = False

            async def start(self) -> None:
                self.started = True

            async def stop(self) -> None:
                self.started = False

            async def publish(self, message: RabbitMQMessage) -> None:
                self.messages.append(message)
        '''
    )


def _ensure_kafka_settings(path: Path, package_name: str) -> None:
    content = path.read_text(encoding="utf-8")
    if "kafka_bootstrap_servers:" in content:
        return

    _insert_block_before_marker_or_anchor(
        path=path,
        block=_kafka_settings_block(package_name),
        markers=[SETTINGS_INTEGRATION_MARKER, SETTINGS_LLM_MARKER],
        anchor="    model_config = SettingsConfigDict(",
    )


def _kafka_settings_block(package_name: str) -> list[str]:
    return [
        "    kafka_enabled: bool = False",
        '    kafka_bootstrap_servers: str = "localhost:9092"',
        f'    kafka_client_id: str = "{package_name}"',
        f'    kafka_default_topic: str = "{package_name}.events"',
        f'    kafka_group_id: str = "{package_name}"',
        '    kafka_auto_offset_reset: str = "earliest"',
        '    kafka_acks: str = "all"',
        "    kafka_compression_type: str | None = None",
        "    kafka_request_timeout_ms: int = 40000",
    ]


def _ensure_kafka_env(path: Path, package_name: str) -> None:
    content = path.read_text(encoding="utf-8")
    if "KAFKA_BOOTSTRAP_SERVERS=" in content:
        return

    _insert_block_before_marker_or_anchor(
        path=path,
        block=_kafka_env_block(package_name),
        markers=[ENV_INTEGRATION_MARKER, ENV_LLM_MARKER],
        anchor=None,
    )


def _kafka_env_block(package_name: str) -> list[str]:
    return [
        "KAFKA_ENABLED=false",
        "KAFKA_BOOTSTRAP_SERVERS=localhost:9092",
        f"KAFKA_CLIENT_ID={package_name}",
        f"KAFKA_DEFAULT_TOPIC={package_name}.events",
        f"KAFKA_GROUP_ID={package_name}",
        "KAFKA_AUTO_OFFSET_RESET=earliest",
        "KAFKA_ACKS=all",
        "# KAFKA_COMPRESSION_TYPE=",
        "KAFKA_REQUEST_TIMEOUT_MS=40000",
    ]


def _ensure_rabbitmq_settings(path: Path, package_name: str) -> None:
    content = path.read_text(encoding="utf-8")
    if "rabbitmq_url:" in content:
        return

    _insert_block_before_marker_or_anchor(
        path=path,
        block=_rabbitmq_settings_block(package_name),
        markers=[SETTINGS_INTEGRATION_MARKER, SETTINGS_LLM_MARKER],
        anchor="    model_config = SettingsConfigDict(",
    )


def _rabbitmq_settings_block(package_name: str) -> list[str]:
    return [
        "    rabbitmq_enabled: bool = False",
        '    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"',
        f'    rabbitmq_client_id: str = "{package_name}"',
        f'    rabbitmq_exchange: str = "{package_name}.events"',
        '    rabbitmq_exchange_type: str = "topic"',
        "    rabbitmq_exchange_durable: bool = True",
        f'    rabbitmq_default_routing_key: str = "{package_name}.event"',
        f'    rabbitmq_default_queue: str = "{package_name}.events"',
        "    rabbitmq_queue_durable: bool = True",
        "    rabbitmq_prefetch_count: int = 10",
    ]


def _ensure_rabbitmq_env(path: Path, package_name: str) -> None:
    content = path.read_text(encoding="utf-8")
    if "RABBITMQ_URL=" in content:
        return

    _insert_block_before_marker_or_anchor(
        path=path,
        block=_rabbitmq_env_block(package_name),
        markers=[ENV_INTEGRATION_MARKER, ENV_LLM_MARKER],
        anchor=None,
    )


def _rabbitmq_env_block(package_name: str) -> list[str]:
    return [
        "RABBITMQ_ENABLED=false",
        "RABBITMQ_URL=amqp://guest:guest@localhost:5672/",
        f"RABBITMQ_CLIENT_ID={package_name}",
        f"RABBITMQ_EXCHANGE={package_name}.events",
        "RABBITMQ_EXCHANGE_TYPE=topic",
        "RABBITMQ_EXCHANGE_DURABLE=true",
        f"RABBITMQ_DEFAULT_ROUTING_KEY={package_name}.event",
        f"RABBITMQ_DEFAULT_QUEUE={package_name}.events",
        "RABBITMQ_QUEUE_DURABLE=true",
        "RABBITMQ_PREFETCH_COUNT=10",
    ]


def _ensure_project_dependency(path: Path, dependency: str | None) -> None:
    if dependency is None:
        return

    content = path.read_text(encoding="utf-8")
    dependency_line = f'    "{dependency}",'

    if dependency_line in content:
        return

    lines = content.splitlines()
    start_index = _find_line_index(lines, "dependencies = [", path)
    end_index = _find_array_end_index(lines, start_index, path)

    entries = [line for line in lines[start_index + 1 : end_index] if line.strip()]
    entries.append(dependency_line)
    entries.sort(key=lambda line: line.strip().lower())

    lines[start_index + 1 : end_index] = entries
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _insert_block_before_marker_or_anchor(
    *,
    path: Path,
    block: list[str],
    markers: list[str],
    anchor: str | None,
) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()

    insert_at = None
    for marker in markers:
        if marker in lines:
            insert_at = lines.index(marker)
            break

    if insert_at is None and anchor and anchor in lines:
        insert_at = lines.index(anchor)

    if insert_at is None:
        insert_at = len(lines)

    lines[insert_at:insert_at] = block + [""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _find_line_index(lines: list[str], line: str, path: Path) -> int:
    try:
        return lines.index(line)
    except ValueError as exc:
        raise RuntimeError(f"Unsupported dependency layout: {path}") from exc


def _find_array_end_index(lines: list[str], start_index: int, path: Path) -> int:
    for index in range(start_index + 1, len(lines)):
        if lines[index] == "]":
            return index

    raise RuntimeError(f"Unsupported dependency layout: {path}")
