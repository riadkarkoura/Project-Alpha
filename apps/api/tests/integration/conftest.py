from collections.abc import AsyncIterator

import asyncpg
import pytest

from app.core.config import settings
from app.infrastructure.database.connection import init_connection


class SingleConnectionPool:
    """Mimics the asyncpg.Pool.acquire() interface used by the repositories, but
    always hands back the same connection so a whole test runs inside one
    transaction that the fixture rolls back afterward.
    """

    def __init__(self, connection: asyncpg.Connection) -> None:
        self._connection = connection

    def acquire(self) -> "SingleConnectionPool":
        return self

    async def __aenter__(self) -> asyncpg.Connection:
        return self._connection

    async def __aexit__(self, *exc_info: object) -> None:
        return None


@pytest.fixture
async def db_pool() -> AsyncIterator[SingleConnectionPool]:
    try:
        connection = await asyncpg.connect(dsn=settings.database_url)
    except (OSError, asyncpg.PostgresError) as exc:
        pytest.skip(f"Postgres is not reachable at {settings.database_url}: {exc}")

    await init_connection(connection)

    transaction = connection.transaction()
    await transaction.start()

    try:
        yield SingleConnectionPool(connection)
    finally:
        await transaction.rollback()
        await connection.close()
