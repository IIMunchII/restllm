import redis.asyncio as redis
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse

from ..dependencies import get_redis_client, get_user
from ..models import ChatMessage, CRUDAction, Event, EventStatus, EventType
from ..redis.events import create_events_list, publish_event, subscribe_event

router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.get("/{event_type}")
async def events(
    request: Request,
    event_type: EventType,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    events_list = create_events_list(get_user(request), [event_type])

    return StreamingResponse(
        subscribe_event(
            events_list,
            redis_client,
        ),
        media_type="text/event-stream",
    )


@router.post("/create")
async def create_event(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis_client),
):
    event = Event(
        action=CRUDAction.CREATE,
        status=EventStatus.COMPLETED,
        object=ChatMessage(role="user", content="Hallo world"),
    )
    return await publish_event(
        event=event,
        owner=get_user(request),
        redis_client=redis_client,
    )
