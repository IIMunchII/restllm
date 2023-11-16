from redis.commands.search.query import Query
from enum import StrEnum, auto
from ..models import User


class SortingField(StrEnum):
    CREATED_AT = auto()
    UPDATED_AT = auto()
    ID = auto()


def create_privat_query(
    owner: User,
) -> Query:
    return Query(f"@owner:[{owner.id} {owner.id}]").dialect(3)


def add_pagination_to_query(
    query: Query,
    offset: int,
    limit: int,
) -> Query:
    return query.paging(offset, limit)


def add_sorting_to_query(
    query: Query,
    sorting_field: SortingField,
    ascending: bool,
) -> Query:
    return query.sort_by(str(sorting_field), asc=ascending)
