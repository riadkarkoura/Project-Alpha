from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.infrastructure.database.connection import close_pool
from app.presentation.api.v1 import router as api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await close_pool()


app = FastAPI(title="Project Alpha API", lifespan=lifespan)
app.include_router(api_v1_router)
