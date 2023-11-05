import redis.asyncio as redis
import redis.exceptions
from fastapi import APIRouter, Depends

from ..dependencies import get_redis_client, build_get_instance_key
from ..exceptions import ObjectNotFoundException
from ..models import Chat, ChatMessage, ChatWithMeta
from ..redis.commands import append_chat_message, edit_chat_message
from ..types import paths

router = APIRouter()


@router.patch(
    "/messages/{index}",
    response_model=ChatWithMeta,
    description="Edit chat message at index",
)
async def update_chat_message(
    chat_message: ChatMessage,
    index: int = paths.index_path,
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_instance_key(Chat)),
):
    updated, updated_at, instance = await edit_chat_message(
        redis_client=redis_client,
        instance=chat_message,
        index=index,
        key=key,
    )
    if not updated and not updated_at:
        raise ObjectNotFoundException(ChatMessage)
    return instance


@router.post(
    "/messages",
    response_model=ChatWithMeta,
    description="Append user message to chat. Operation does not run completetion",
)
async def add_chat_message(
    chat_message: ChatMessage,
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_instance_key(Chat)),
):
    try:
        updated, updated_at, instance = await append_chat_message(
            redis_client=redis_client,
            instance=chat_message,
            key=key,
        )
        return instance
    except redis.exceptions.ResponseError as exec:
        raise ObjectNotFoundException(Chat) from exec
