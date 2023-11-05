import redis.asyncio as redis

from litellm import acompletion

from ..models import ChatMessage, ChatWithMeta
from ..models.functions import get_function_schemas
from ..redis.commands import append_chat_message


async def chat_acompletion_call(
    chat_with_meta: ChatWithMeta,
    redis_client: redis.Redis,
    key: str,
):
    parameters = chat_with_meta.object.model_dump(mode="json")

    function_names = parameters.get("completion_parameters").pop("functions", [])
    function_schemas = get_function_schemas(function_names)

    response = acompletion(
        **parameters.get("completion_parameters"),
        functions=function_schemas,
        messages=parameters.get("messages"),
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
