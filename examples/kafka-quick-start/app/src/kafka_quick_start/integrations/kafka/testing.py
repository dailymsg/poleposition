from kafka_quick_start.integrations.kafka.schemas import KafkaEvent


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
