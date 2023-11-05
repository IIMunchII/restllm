import redis.asyncio as redis
from cryptography.fernet import Fernet


async def get_fernet(
    redis_client: redis.Redis,
    key_name: str = "fernet_crypto_key",
    expiration_time: int = 3600,
) -> Fernet:
    fernet_key = await redis_client.get(key_name)

    if fernet_key is None:
        fernet_key = Fernet.generate_key().decode()
        await redis_client.setex(key_name, expiration_time, fernet_key)
    else:
        fernet_key = fernet_key.decode()
        await redis_client.expire(key_name, expiration_time)

    return Fernet(fernet_key)
