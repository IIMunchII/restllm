import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, status

from ..cryptography.keys import get_fernet
from ..cryptography.secure_url import (
    decrypt_payload,
    generate_secure_url,
    payload_is_valid,
)
from ..dependencies import get_redis_client, get_shareable_key
from ..models import MetaModel
from ..models.share import ShareableObject, ShareableObject
from ..redis.commands import copy_instance
from ..settings import settings
from ..types import paths

router = APIRouter(
    prefix=settings.share_prefix,
    tags=["shares"],
)


@router.get("/{class_name}/{id}/generate")
async def generate_shared_object(
    redis_client: redis.Redis = Depends(get_redis_client),
    shareable_key: str = Depends(get_shareable_key),
) -> ShareableObject:
    token = await copy_instance(
        redis_client=redis_client,
        source_key=shareable_key,
        expire_time=settings.shared_object_expire,
    )
    fernet = await get_fernet(redis_client)
    signed_url = generate_secure_url(fernet, {"token": token})
    signed_url.update(expire_time=settings.shared_object_expire)
    return signed_url


@router.get("/{payload}/{signature}")
async def get_shared_object(
    payload: str = paths.payload_path,
    signature: str = paths.signature_path,
    redis_client: redis.Redis = Depends(get_redis_client),
) -> MetaModel:
    fernet = await get_fernet(redis_client)
    if not payload_is_valid(payload, signature):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request",
        )
    token: str = decrypt_payload(fernet, payload).get("token")
    instance = await redis_client.json().get(token)
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shared object has expired",
        )
    return instance
