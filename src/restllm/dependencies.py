import redis.asyncio as redis

from fastapi import Depends, Form
from jose import JWTError, ExpiredSignatureError, jwt
from typing import Type
from pydantic import SecretStr, EmailStr

from .models.base import User
from .settings import settings
from .types import paths
from .models.share import ShareableObject
from .redis.keys import get_class_name
from .redis.commands import get_instance
from .cryptography.authentication import verify_password
from .models.authentication import UserWithPasswordHash, UserSignUp, get_user_email_key
from .exceptions import InvalidCredentialsException, TokenExpiredException
from .cryptography.authentication import oauth2_scheme
from .settings import settings

connection_pool: redis.ConnectionPool = None


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


async def get_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = await decode_user_token(token)
    return User(**payload)


async def decode_user_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        payload.pop("exp")
        if not payload:
            raise InvalidCredentialsException
        return payload
    except ExpiredSignatureError:
        raise TokenExpiredException
    except JWTError:
        raise InvalidCredentialsException


async def get_user_with_password_hash(
    email: EmailStr,
    redis_client: redis.Redis = Depends(get_redis_client),
) -> dict | None:
    user_id: bytes = await redis_client.get(get_user_email_key(email))
    user_instance = await get_instance(
        redis_client,
        key=f"{get_class_name(User)}:{user_id.decode()}",
    )
    return user_instance


async def get_shareable_key(
    object: ShareableObject,
    id: int = paths.id_path,
    user: User = Depends(get_user),
):
    return f"{object.value}:{user.id}:{id}"


async def authenticate_user(
    email: str,
    password: str,
    redis_client: redis.Redis,
) -> UserWithPasswordHash | bool:
    user = await get_user_with_password_hash(
        email,
        redis_client,
    )
    if not user or not verify_password(password, user.get("hashed_password")):
        raise InvalidCredentialsException
    return UserWithPasswordHash(**user)


async def signup_form(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: EmailStr = Form(...),
    password: SecretStr = Form(...),
) -> UserSignUp:
    return UserSignUp(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )


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
