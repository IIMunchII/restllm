import redis.asyncio as redis

from ..models import EventType, EventWithMeta, User, Event

STOPWORD = "STOP"


def create_events_list(owner: User, event_types: list[EventType]) -> list[str]:
    return [f"{event_type.value}:{owner.id}" for event_type in event_types]


async def subscribe_event(
    events_list: list[str],
    redis_client: redis.Redis,
) -> str:
    async with redis_client.pubsub() as pubsub:
        await pubsub.subscribe(*events_list)
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True, timeout=None
            )
            if message is None:
                continue
            data = message["data"].decode()
            if data == STOPWORD:
                break
            yield data + "\n"


async def publish_event(
    event: Event,
    owner: User,
    redis_client: redis.Redis,
    event_type: EventType = EventType.OBJECT,
):
    event_with_meta = EventWithMeta(
        owner=owner.id,
        type=event_type,
        event=event,
    )

    return await event_with_meta.publish(redis_client)
