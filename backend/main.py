
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.lifespan import startup, shutdown
from app.api.router import router as main_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup(app)
    yield
    await shutdown(app)

app = FastAPI(lifespan=lifespan)

app.include_router(main_router)
