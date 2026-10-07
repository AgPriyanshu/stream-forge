from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import models  # noqa: F401
from settings import settings
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession

engine: AsyncEngine = create_async_engine(settings.database_url, echo=True)


async def get_session() -> AsyncGenerator[SQLModelAsyncSession, None]:
    async with SQLModelAsyncSession(engine) as session:
        yield session


@asynccontextmanager
async def db_session(*, expire_on_commit: bool = True):
    async with SQLModelAsyncSession(
        engine, expire_on_commit=expire_on_commit
    ) as session:
        yield session
