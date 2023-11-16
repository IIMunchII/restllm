from typing import Optional, Type

import redis.asyncio as redis
import redis.exceptions
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel

from ..dependencies import (
    get_redis_client,
    get_user,
    build_get_new_instance_key,
    build_get_instance_key,
)
from ..exceptions import IndexNotImplemented, ObjectNotFoundException
from ..models import User
from ..redis.commands import (
    create_instance,
    delete_instance,
    get_instance,
    update_instance,
)
from ..redis.keys import get_class_name
from ..redis.search import SortingField, list_instances
from ..types import queries


def build_get_instance_endpoint(cls: Type):
    async def get_instance_endpoint(
        redis_client: redis.Redis = Depends(get_redis_client),
        key: str = Depends(build_get_instance_key(cls)),
    ):
        instance = await get_instance(
            redis_client=redis_client,
            key=key,
        )
        if not instance:
            raise ObjectNotFoundException(cls)
        return instance

    return get_instance_endpoint


def build_create_instance_endpoint(cls: Type):
    async def create_instance_endpoint(
        instance: cls,
        redis_client: redis.Redis = Depends(get_redis_client),
        new_key: tuple[str, int] = Depends(build_get_new_instance_key(cls)),
        user: User = Depends(get_user),
    ):
        created, instance = await create_instance(
            redis_client=redis_client,
            owner=user,
            instance=instance,
            key=new_key[0],
            instance_id=new_key[1],
        )
        if not created:
            raise HTTPException(
                status_code=422,
                detail=f"Ressource of type '{get_class_name(cls)}' could not be created.",
            )
        return instance

    return create_instance_endpoint


def build_update_instance_endpoint(cls: Type):
    async def update_instance_endpoint(
        instance: cls,
        redis_client: redis.Redis = Depends(get_redis_client),
        key: str = Depends(build_get_instance_key(cls)),
    ):
        updated, updated_at, instance = await update_instance(
            redis_client=redis_client,
            instance=instance,
            key=key,
        )
        if not updated and not updated_at:
            raise ObjectNotFoundException(cls)
        return instance

    return update_instance_endpoint


def build_delete_instance_endpoint(cls: Type):
    async def delete_instance_endpoint(
        redis_client: redis.Redis = Depends(get_redis_client),
        key: str = Depends(build_get_instance_key(cls)),
    ):
        deleted = await delete_instance(
            redis_client=redis_client,
            key=key,
        )
        if deleted:
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise ObjectNotFoundException(cls)

    return delete_instance_endpoint


def build_list_instances_endpoint(cls: Type):
    async def list_instances_endpoint(
        offset: Optional[int] = queries.offset_query,
        limit: Optional[int] = queries.limit_query,
        sorting_field: Optional[SortingField] = queries.sorting_field_query,
        ascending: Optional[bool] = queries.ascending_query,
        redis_client: redis.Redis = Depends(get_redis_client),
        user: User = Depends(get_user),
    ):
        try:
            return await list_instances(
                redis_client,
                class_name=get_class_name(cls),
                owner=user,
                offset=offset,
                limit=limit,
                sorting_field=sorting_field,
                ascending=ascending,
            )
        except redis.exceptions.ResponseError as exec:
            if str(exec).endswith("no such index"):
                raise IndexNotImplemented(cls) from exec
            else:
                raise exec

    return list_instances_endpoint


def add_crud_route(
    router: APIRouter,
    instance_model: BaseModel,
    response_model: BaseModel,
    prefix: str = "",
):
    router.add_api_route(
        prefix + "/{id}",
        build_get_instance_endpoint(instance_model),
        response_model=response_model,
        methods=["GET"],
    )
    router.add_api_route(
        prefix,
        build_create_instance_endpoint(instance_model),
        response_model=response_model,
        methods=["POST"],
        status_code=status.HTTP_201_CREATED,
    )
    router.add_api_route(
        prefix + "/{id}",
        build_update_instance_endpoint(instance_model),
        response_model=response_model,
        methods=["PUT"],
    )
    router.add_api_route(
        prefix + "/{id}",
        build_delete_instance_endpoint(instance_model),
        methods=["DELETE"],
        status_code=status.HTTP_204_NO_CONTENT,
    )
    router.add_api_route(
        prefix,
        build_list_instances_endpoint(instance_model),
        response_model=list[response_model],
        methods=["GET"],
    )
