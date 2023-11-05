import redis.asyncio as redis
import redis.exceptions

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from ..dependencies import (
    get_redis_client,
    build_get_instance_key,
)
from ..endpoints.completion import chat_acompletion_call
from ..exceptions import ObjectNotFoundException
from ..models import Chat, ChatMessage, ChatWithMeta, RoleTypes
from ..redis.commands import append_chat_message, get_instance
from ..redis.keys import get_class_name

router = APIRouter()


@router.get(
    "/completion",
    description="Complete a chat from an existing state on server",
)
async def get_completion(
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_instance_key(Chat)),
) -> str:
    instance = await get_instance(
        redis_client=redis_client,
        key=key,
    )
    if not instance:
        raise ObjectNotFoundException(Chat)
    chat_with_meta = ChatWithMeta.model_validate(instance)
    if not chat_with_meta.object.last_message_is_user():
        raise HTTPException(
            status_code=404,
            detail=f"{get_class_name(ChatMessage)} with role {RoleTypes.USER} not found",
        )
    return StreamingResponse(
        chat_acompletion_call(chat_with_meta, redis_client, key),
        media_type="text/event-stream",
    )


@router.post(
    "/completion",
    description="Complete a chat from providet message as string input.",
)
async def post_completion(
    chat_message: ChatMessage,
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_instance_key(Chat)),
) -> str:
    try:
        updated, updated_at, instance = await append_chat_message(
            redis_client=redis_client,
            instance=chat_message,
            key=key,
        )
        chat_with_meta = ChatWithMeta.model_validate(instance)
        return StreamingResponse(
            chat_acompletion_call(chat_with_meta, redis_client, key),
            media_type="text/event-stream",
        )
    except redis.exceptions.ResponseError as exec:
        raise ObjectNotFoundException(Chat) from exec
