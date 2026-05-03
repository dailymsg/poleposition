from {{package_name}}.integrations.kafka.producer import KafkaEventProducer
from {{package_name}}.settings import get_settings


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
