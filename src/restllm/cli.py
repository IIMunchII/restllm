import sys
import time

import click
import redis
import redis.exceptions

from .redis.index import (
    create_index_on_meta_model,
    get_class_from_class_name,
    get_meta_model_schema,
    string_to_class_mapping,
)
from .settings import settings


class IndexAlreadyExists(redis.exceptions.ResponseError):
    pass


@click.group()
def cli():
    pass


@cli.command(name="create_index")
@click.option(
    "--redis-url",
    default=str(settings.redis_dsn),
    help="Redis URL",
)
@click.option(
    "--class-name",
    required=True,
    help="Class name for which index needs to be created",
)
def create_index(redis_url: str, class_name: str):
    redis_client: redis.Redis = redis.from_url(redis_url)
    meta_model_schema = get_meta_model_schema()

    _class = get_class_from_class_name(class_name)

    create_index_on_meta_model(redis_client, meta_model_schema, _class)


@cli.command(name="migrate_all_index")
@click.option(
    "--redis-url",
    default=str(settings.redis_dsn),
    help="Redis URL",
)
def migrate_all_index(redis_url: str):
    redis_client: redis.Redis = redis.from_url(redis_url)
    meta_model_schema = get_meta_model_schema()

    for _class in string_to_class_mapping.values():
        try:
            create_index_on_meta_model(redis_client, meta_model_schema, _class)
        except redis.exceptions.ResponseError as error:
            if str(error) == "Index already exists":
                click.echo(
                    f"Index for model class '{_class.__name__}' already exists. Skipping index creation!",
                    color=True,
                )
            else:
                raise error


@cli.command(name="delete_data")
@click.option(
    "--redis-url",
    default=str(settings.redis_dsn),
    help="Redis URL",
)
def delete_data(redis_url: str):
    response = input(
        f"Are you sure you want to DELETE ALL data in redis database '{redis_url}'?: Choices: (yes/y, no/n)\nAnswer: "
    )
    if response in {"Yes", "yes", "y", "Y"}:
        redis_client: redis.Redis = redis.from_url(redis_url)
        redis_client.flushall()
        click.echo(f"Deleted all data")
    else:
        click.echo(f"Aborted deletion")


@cli.command(name="connection_count")
@click.option(
    "--redis-url",
    default=str(settings.redis_dsn),
    help="Redis URL",
)
def connection_count(redis_url: str):
    redis_client: redis.Redis = redis.from_url(redis_url)
    while True:
        connection_count = len(redis_client.client_list())
        sys.stdout.write(f"\rCurrent connection count: {connection_count - 1}")
        sys.stdout.flush()
        time.sleep(1)


if __name__ == "__main__":
    cli()
