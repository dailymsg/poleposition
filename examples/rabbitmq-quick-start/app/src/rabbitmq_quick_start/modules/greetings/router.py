from fastapi import APIRouter, status

from rabbitmq_quick_start.integrations.rabbitmq.factory import (
    build_rabbitmq_event_publisher,
)
from rabbitmq_quick_start.modules.greetings.schemas import (
    GreetingRequest,
    GreetingResponse,
)
from rabbitmq_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)
from rabbitmq_quick_start.settings import get_settings


router = APIRouter()


@router.post(
    "/send",
    response_model=GreetingResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_greeting(payload: GreetingRequest) -> GreetingResponse:
    settings = get_settings()
    publisher = build_rabbitmq_event_publisher()

    await publisher.start()
    try:
        message = await publish_greeting(
            publisher,
            routing_key=settings.rabbitmq_default_routing_key,
            recipient=payload.recipient,
            message=payload.message,
        )
    finally:
        await publisher.stop()

    return GreetingResponse(
        routing_key=message.routing_key,
        message=payload.message,
        status="published",
    )
