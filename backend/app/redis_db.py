from arq.connections import create_pool, RedisSettings
from fastapi import Response
from app.variables import REDIS_HOST, REDIS_PORT
from contextlib import asynccontextmanager


async def init_redis():
    settings = RedisSettings(
        host=REDIS_HOST,
        port=REDIS_PORT,
        database=0
    )
    return await create_pool(settings)


@asynccontextmanager
async def redis_lock(redis, key: str, ttl=30):  # type: ignore
    if await redis.get(key):  # type: ignore
        yield Response(status_code=204)
        return

    await redis.set(key, "1", ex=ttl)  # type: ignore
    try:
        yield
    finally:
        await redis.delete(key)  # type: ignore
