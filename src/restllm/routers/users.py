import redis.asyncio as redis
import redis.exceptions
from fastapi import APIRouter, Depends, Request, Response, status

from ..dependencies import (
    get_redis_client,
    get_user,
    build_get_new_class_user_key,
    build_get_class_user_key,
)
from ..exceptions import ObjectNotFoundException, ObjectAlreadyExistsException
from ..models import UserProfile, UserProfileWithMeta, User
from ..redis.commands import create_instance, update_instance

router = APIRouter(
    prefix="/user",
    tags=["users"],
)


@router.get("", response_model=User)
async def get_user_profile(request: Request):
    return get_user(request)


@router.get("/profile", response_model=UserProfileWithMeta)
async def get_user_profile(
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_class_user_key(UserProfile)),
):
    instance = await redis_client.json().get(key)
    if not instance:
        raise ObjectNotFoundException(UserProfile)
    return instance


@router.post(
    "/profile",
    response_model=UserProfileWithMeta,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_profile(
    user_profile: UserProfile,
    user: User = Depends(get_user),
    redis_client: redis.Redis = Depends(get_redis_client),
    new_key: str = Depends(build_get_new_class_user_key(UserProfile)),
):
    new_key, instance_id = new_key
    profile_exists = await redis_client.exists(new_key)
    if profile_exists:
        raise ObjectAlreadyExistsException(UserProfile)
    created, instance = await create_instance(
        redis_client=redis_client,
        owner=user,
        instance=user_profile,
        instance_id=instance_id,
        key=new_key,
    )
    return instance


@router.put("/profile", response_model=UserProfileWithMeta)
async def update_user_profile(
    user_profile: UserProfile,
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_class_user_key(UserProfile)),
):
    updated, updated_at, instance = await update_instance(
        redis_client=redis_client,
        instance=user_profile,
        key=key,
    )
    if not updated and not updated_at:
        raise ObjectNotFoundException(UserProfile)
    return instance


@router.delete("/profile", status_code=204)
async def delete_user_profile(
    request: Request,
    redis_client: redis.Redis = Depends(get_redis_client),
    key: str = Depends(build_get_class_user_key(UserProfile)),
):
    deleted = await redis_client.delete(key)
    if deleted:
        return Response(status_code=204)
    else:
        raise ObjectNotFoundException(UserProfile)
