import secrets

import redis.asyncio as redis
from pydantic import BaseModel
from redis.commands.json.path import Path

from ..models import ChatMessage, Datetime, MetaModel, User


async def get_multiple_instances(
    redis_client: redis.Redis,
    keys: list[str],
) -> dict:
    return await redis_client.json().mget(keys)


async def get_instance(
    redis_client: redis.Redis,
    key: str,
) -> dict:
    return await redis_client.json().get(key)


async def copy_instance(
    redis_client: redis.Redis,
    source_key: str,
    expire_time: int,
) -> tuple[bool, bool, str]:
    token = secrets.token_urlsafe(32)
    async with redis_client.pipeline() as pipeline:
        pipeline.multi()
        (
            pipeline.copy(
                source=source_key,
                destination=token,
            ),
            pipeline.expire(token, time=expire_time, nx=True),
        )
        copied, expired = await pipeline.execute()
    return copied, expired, token


async def create_instance(
    redis_client: redis.Redis,
    owner: User,
    instance: BaseModel,
    instance_id: int,
    key: str,
) -> tuple[bool, MetaModel]:
    datetime_instance = Datetime()

    meta_instance = MetaModel(
        id=instance_id,
        class_name=instance.__class__.__name__,
        owner=owner.id,
        object=instance,
        created_at=datetime_instance,
        updated_at=datetime_instance,
    )

    created = await redis_client.json().set(
        key,
        Path.root_path(),
        meta_instance.model_dump(mode="json"),
        nx=True,
    )
    return created, meta_instance


async def update_instance(
    redis_client: redis.Redis,
    instance: BaseModel,
    key: str,
) -> list[bool, bool, dict]:
    async with redis_client.pipeline() as pipeline:
        pipeline.multi()
        (
            pipeline.json().set(
                key,
                "$.object",
                instance.model_dump(mode="json"),
                xx=True,
            ),
            pipeline.json().set(
                key,
                "$.updated_at",
                Datetime().model_dump(mode="json"),
                xx=True,
            ),
            pipeline.json().get(key),
        )
        return await pipeline.execute()


async def delete_instance(
    redis_client: redis.Redis,
    key: str,
) -> bool:
    return await redis_client.delete(key)


async def edit_chat_message(
    redis_client: redis.Redis,
    instance: ChatMessage,
    index: int,
    key: str,
) -> list[bool, bool, dict]:
    async with redis_client.pipeline() as pipeline:
        pipeline.multi()
        (
            pipeline.json().set(
                key,
                f"$.object.messages[{index}]",
                instance.model_dump(mode="json"),
                xx=True,
            ),
            pipeline.json().set(
                key,
                "$.updated_at",
                Datetime().model_dump(mode="json"),
                xx=True,
            ),
            pipeline.json().get(key),
        )
        return await pipeline.execute()


async def append_chat_message(
    redis_client: redis.Redis,
    instance: ChatMessage,
    key: str,
) -> list[bool, bool, dict]:
    async with redis_client.pipeline() as pipeline:
        pipeline.multi()
        (
            pipeline.json().arrappend(
                key,
                f"$.object.messages",
                instance.model_dump(mode="json"),
            ),
            pipeline.json().set(
                key,
                "$.updated_at",
                Datetime().model_dump(mode="json"),
                xx=True,
            ),
            pipeline.json().get(key),
        )
        return await pipeline.execute()
