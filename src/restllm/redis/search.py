import json

import redis.asyncio as redis
from redis.commands.search.query import Query

from .index import get_index_key
from .queries import (
    SortingField,
    add_pagination_to_query,
    add_sorting_to_query,
    create_privat_query,
)


async def search_index(
    redis_client: redis.Redis, query: Query, class_name: str
) -> list[dict]:
    index = redis_client.ft(get_index_key(class_name))
    result = await index.search(query)
    return [json.loads(item["json"])[0] for item in result.docs]


async def list_instances(
    redis_client: redis.Redis,
    class_name: str,
    owner: str,
    offset: int | None = None,
    limit: int | None = None,
    sorting_field: SortingField | None = None,
    ascending: bool = True,
) -> list[dict]:
    query = create_privat_query(owner)
    if offset >= 0 and limit > 0:
        query = add_pagination_to_query(query, offset, limit)
    if sorting_field:
        query = add_sorting_to_query(query, sorting_field, ascending)
    return await search_index(redis_client, query, class_name)
