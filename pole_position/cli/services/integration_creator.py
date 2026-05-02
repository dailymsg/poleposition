from pathlib import Path
from textwrap import dedent

from pole_position.cli.services.project_locator import find_package_root, find_project_root


SUPPORTED_INTEGRATIONS = ("kafka",)

SETTINGS_INTEGRATION_MARKER = "    # polepos:integration-settings"
SETTINGS_LLM_MARKER = "    # polepos:llm-settings"
ENV_INTEGRATION_MARKER = "# polepos:integration-env"
ENV_LLM_MARKER = "# polepos:llm-env"


def add_integration(integration_name: str, cwd: Path | None = None) -> None:
    if integration_name not in SUPPORTED_INTEGRATIONS:
        supported = ", ".join(SUPPORTED_INTEGRATIONS)
        raise ValueError(
            f"Unsupported integration '{integration_name}'. Expected one of: {supported}."
        )

    project_root = find_project_root(cwd)
    package_root = find_package_root(cwd)
    package_name = package_root.name
    integration_root = package_root / "integrations" / integration_name

    _validate_add_integration_preflight(
        project_root=project_root,
        package_root=package_root,
        integration_root=integration_root,
        integration_name=integration_name,
    )

    _ensure_integration_files(package_root, package_name)
    _ensure_kafka_settings(package_root / "settings.py", package_name)
    _ensure_kafka_env(project_root / ".env.example", package_name)
    _ensure_project_dependency(project_root / "pyproject.toml", "aiokafka>=0.12.0")


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


def _ensure_integration_files(package_root: Path, package_name: str) -> None:
    for relative_path, content in _kafka_integration_files(package_name).items():
        path = package_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists():
            path.write_text(content, encoding="utf-8")


def _kafka_integration_files(package_name: str) -> dict[str, str]:
    return {
        "integrations/__init__.py": "",
        "integrations/kafka/__init__.py": _render_kafka_init(package_name),
        "integrations/kafka/consumer.py": _render_kafka_consumer(package_name),
        "integrations/kafka/factory.py": _render_kafka_factory(package_name),
        "integrations/kafka/producer.py": _render_kafka_producer(package_name),
        "integrations/kafka/schemas.py": _render_kafka_schemas(),
        "integrations/kafka/testing.py": _render_kafka_testing(package_name),
    }


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


def _ensure_project_dependency(path: Path, dependency: str) -> None:
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
