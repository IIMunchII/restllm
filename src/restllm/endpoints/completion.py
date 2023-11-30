import redis.asyncio as redis

from litellm import acompletion

from ..models import ChatMessage, ChatWithMeta
from ..redis.commands import append_chat_message


async def chat_acompletion_call(
    chat_with_meta: ChatWithMeta,
    redis_client: redis.Redis,
    key: str,
):
    kwargs = chat_with_meta.object.dump_json_for_completion()
    response = acompletion(
        **kwargs,
        stream=True,
    )
    chat_message = ChatMessage(role="assistant", content="")
    async for chunk in await response:
        next_token = chunk["choices"][0]["delta"].get("content")
        if not next_token:
            continue
        chat_message.content += next_token
        yield next_token
    await append_chat_message(
        redis_client=redis_client,
        instance=chat_message,
        key=key,
    )
