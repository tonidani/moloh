from fastapi import FastAPI

from app.database import init_db
from app.redis_db import init_redis


async def startup(app: FastAPI) -> None:
    app.state.db = await init_db(True)
    app.state.redis = await init_redis()


async def shutdown(app: FastAPI) -> None:
    await app.state.db.close()
    await app.state.redis.close()
