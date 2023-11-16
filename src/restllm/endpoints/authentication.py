import redis.asyncio as redis
from ..models.authentication import UserWithPasswordHash
from redis.commands.json.path import Path


async def create_user_instance(
    redis_client: redis.Redis,
    instance: UserWithPasswordHash,
    email_key: str,
) -> tuple[bool, dict]:
    key = f"User:{instance.id}"

    async with redis_client.pipeline() as pipeline:
        pipeline.multi()
        (
            pipeline.json().set(
                key,
                Path.root_path(),
                instance.model_dump(mode="json"),
                nx=True,
            ),
            pipeline.set(
                email_key,
                instance.id,
                nx=True,
            ),
        )
        result = await pipeline.execute()
    return all(result), instance
