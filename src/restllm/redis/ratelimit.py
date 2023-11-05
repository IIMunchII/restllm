import redis.asyncio as redis
import time

from ..models import User

CALLS_PER_MINUTE_LIMIT = 25

MILLISECONDS_IN_DAY = 86_400_000
MILLISECONDS_IN_MINUTE = 60_000
MILLISECONDS_IN_HOUR = 3_600_000


async def check_rate_limit(
    redis_client: redis.Redis,
    user: User,
    api_path: str,
    route_weight_score: int = 1,
) -> str:
    epoch_ms = get_current_epoch_milliseconds()
    rate_limit_key = f"ratelimit:{user.id}:{api_path}"
    async with redis_client.pipeline() as pipeline:
        pipeline.multi()

        remove_old_entries(pipeline, rate_limit_key, epoch_ms - MILLISECONDS_IN_MINUTE)
        add_new_entry(pipeline, rate_limit_key, epoch_ms, route_weight_score)
        get_all_entries(pipeline, rate_limit_key)
        set_expiration(pipeline, rate_limit_key, MILLISECONDS_IN_MINUTE)

        result = await pipeline.execute()
        return is_rate_limited(calculate_rate_limit_score(result))


def get_current_epoch_milliseconds():
    return int(time.time() * 1000)


def remove_old_entries(
    pipeline: redis.Redis,
    key: str,
    old_score_threshold: int,
):
    pipeline.zremrangebyscore(key, 0, old_score_threshold)


def add_new_entry(
    pipeline: redis.Redis,
    key: str,
    epoch_ms: int,
    route_weight_score: int,
):
    value = f"{epoch_ms}:{route_weight_score}"
    pipeline.zadd(key, {value: epoch_ms})


def get_all_entries(
    pipeline: redis.Redis,
    key: str,
):
    pipeline.zrange(key, 0, -1)


def set_expiration(
    pipeline: redis.Redis,
    key: str,
    expiration_ms: int,
):
    pipeline.expire(key, expiration_ms)


def calculate_rate_limit_score(entries: list[bytes]):
    return sum(int(entry.decode("utf-8").split(":")[-1]) for entry in entries)


def is_rate_limited(score: int):
    return score > CALLS_PER_MINUTE_LIMIT
