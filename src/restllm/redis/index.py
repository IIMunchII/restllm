from typing import Any, Type

import redis
import redis.exceptions
from redis.commands.search.field import NumericField, TextField
from redis.commands.search.indexDefinition import IndexDefinition, IndexType

from ..models import Chat, Prompt, PromptTemplate, CompletionParameters
from ..redis.keys import get_class_name

string_to_class_mapping = {
    "PromptTemplate": PromptTemplate,
    "Chat": Chat,
    "Prompt": Prompt,
    "CompletionParameters": CompletionParameters,
}


class IndexClassDoesNotExist(KeyError):
    pass


class IndexNotFound(redis.exceptions.ResponseError):
    pass


def get_class_from_class_name(class_name: str) -> dict[str, Type]:
    try:
        return string_to_class_mapping[class_name]
    except KeyError as exec:
        raise IndexClassDoesNotExist(
            f"The class '{class_name}' is not registeret for indexing"
        ) from exec


def get_meta_model_schema():
    return (
        NumericField("$.owner", as_name="owner"),
        NumericField("$.id", as_name="id"),
        NumericField("$.created_at.timestamp", as_name="created_at"),
        NumericField("$.updated_at.timestamp", as_name="updated_at"),
    )


def get_prompt_schema():
    return (
        TextField("$.object.description"),
        TextField("$.object.name"),
    )


def get_index_key_from_class(_class: Type):
    return get_index_key(get_class_name(_class))


def get_index_key(class_name: str):
    return f"meta_model_index:{class_name}"


def get_index_prefix(_class: Type):
    return f"{get_class_name(_class)}:"


def create_index_on_meta_model(
    redis_client: redis.Redis,
    meta_model_schema: tuple,
    _class: Type,
) -> Any:
    index = get_index(_class, redis_client)
    return index.create_index(
        meta_model_schema,
        definition=IndexDefinition(
            prefix=[get_index_prefix(_class)], index_type=IndexType.JSON
        ),
    )


def get_index(_class: type, redis_client: redis.Redis):
    return redis_client.ft(get_index_key_from_class(_class))
