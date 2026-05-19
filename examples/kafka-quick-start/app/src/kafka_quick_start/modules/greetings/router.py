from fastapi import APIRouter, status

from kafka_quick_start.integrations.kafka.factory import build_kafka_event_producer
from kafka_quick_start.modules.greetings.schemas import (
    GreetingRequest,
    GreetingResponse,
)
from kafka_quick_start.modules.greetings.services.greetings_service import (
    publish_greeting,
)
from kafka_quick_start.settings import get_settings


router = APIRouter()


@router.post(
    "/send",
    response_model=GreetingResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_greeting(payload: GreetingRequest) -> GreetingResponse:
    settings = get_settings()
    producer = build_kafka_event_producer()

    await producer.start()
    try:
        event = await publish_greeting(
            producer,
            topic=settings.kafka_default_topic,
            recipient=payload.recipient,
            message=payload.message,
        )
    finally:
        await producer.stop()

    return GreetingResponse(
        topic=event.topic,
        key=event.key or "",
        message=payload.message,
        status="published",
    )
