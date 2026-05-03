from {{package_name}}.integrations.rabbitmq.schemas import RabbitMQMessage


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
