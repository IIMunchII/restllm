import redis.asyncio as redis

from fastapi import Request, Depends
from typing import Type

from .models.base import User
from .settings import settings
from .types import paths
from .models.share import ShareableObject
from .redis.keys import get_class_name

connection_pool: redis.ConnectionPool = None


def get_user(request: Request) -> User:
    return request.state.user


async def startup():
    global connection_pool
    connection_pool = redis.ConnectionPool.from_url(str(settings.redis_dsn))


async def shutdown():
    await connection_pool.aclose()


async def get_redis_client():
    redis_client = redis.Redis.from_pool(connection_pool)
    yield redis_client


async def create_instance_id(redis_client: redis.Redis, class_name: str):
    return await redis_client.incr(f"sequence:{class_name}")


async def get_shareable_key(
    object: ShareableObject,
    id: int = paths.id_path,
    user: User = Depends(get_user),
):
    return f"{object.value}:{user.id}:{id}"


def get_key_with_id(class_name: str, owner: User, instance_id: int):
    return f"{class_name}:{owner.id}:{instance_id}"


def get_single_key(class_name: str, owner: User):
    return f"{class_name}:{owner.id}"


def build_get_new_instance_key(cls: Type):
    async def get_new_instance_key(
        user: User = Depends(get_user),
        redis_client: redis.Redis = Depends(get_redis_client),
    ) -> tuple[str, int]:
        class_name = get_class_name(cls)
        instance_id = await create_instance_id(redis_client, class_name)
        return get_key_with_id(class_name, user, instance_id), instance_id

    return get_new_instance_key


def build_get_instance_key(cls: Type):
    async def get_instance_key(
        id: int = paths.id_path,
        user: User = Depends(get_user),
    ):
        class_name = get_class_name(cls)
        return get_key_with_id(class_name, user, id)

    return get_instance_key


def build_get_new_class_user_key(cls: Type):
    async def get_class_user_key(
        user: User = Depends(get_user),
        redis_client: redis.Redis = Depends(get_redis_client),
    ) -> tuple[str, int]:
        class_name = get_class_name(cls)
        instance_id = await create_instance_id(redis_client, class_name)
        return get_single_key(class_name, user), instance_id

    return get_class_user_key


def build_get_class_user_key(cls: Type):
    async def get_class_user_key(
        user: User = Depends(get_user),
    ):
        class_name = get_class_name(cls)
        return get_single_key(class_name, user)

    return get_class_user_key
