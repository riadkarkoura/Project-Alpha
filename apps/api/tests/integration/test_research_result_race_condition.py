import asyncio

import asyncpg
import pytest

from app.core.config import settings
from app.features.projects.infrastructure.database.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from app.features.research_results.infrastructure.database.repositories.postgres_research_result_repository import (  # noqa: E501
    PostgresResearchResultRepository,
)
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.features.research_sessions.infrastructure.database.repositories.postgres_research_session_repository import (  # noqa: E501
    PostgresResearchSessionRepository,
)


class _DirectConnectionPool:
    """A minimal pool-like wrapper around a single, already-committing
    connection. The rolled-back-transaction `db_pool` fixture used by the
    other integration tests can't reproduce a genuine race (a single
    connection can't run two overlapping transactions), so this test manages
    its own connections and commits, cleaning up manually afterward.
    """

    def __init__(self, connection: asyncpg.Connection) -> None:
        self._connection = connection

    def acquire(self) -> "_DirectConnectionPool":
        return self

    async def __aenter__(self) -> asyncpg.Connection:
        return self._connection

    async def __aexit__(self, *exc_info: object) -> None:
        return None


async def test_concurrent_create_for_same_session_does_not_error_and_converges():
    """Regression test for the get-or-create race: two callers hitting
    GET .../research-result for the same session at the same time must not
    trigger an unhandled unique-violation 500 - the second writer should
    transparently fall back to the row the first writer committed.
    """
    try:
        connection_a = await asyncpg.connect(dsn=settings.database_url)
        connection_b = await asyncpg.connect(dsn=settings.database_url)
    except (OSError, asyncpg.PostgresError) as exc:
        pytest.skip(f"Postgres is not reachable at {settings.database_url}: {exc}")

    pool_a = _DirectConnectionPool(connection_a)
    project = await PostgresProjectRepository(pool_a).create("Kitchen Research")
    session = await PostgresResearchSessionRepository(pool_a).create(
        project.id, Marketplace.AMAZON
    )

    try:
        repository_a = PostgresResearchResultRepository(pool_a)
        repository_b = PostgresResearchResultRepository(_DirectConnectionPool(connection_b))

        results = await asyncio.gather(
            repository_a.create(
                research_session_id=session.id,
                opportunity_score=84,
                demand_level="high",
                competition_level="medium",
                profit_level="good",
                summary="First writer.",
            ),
            repository_b.create(
                research_session_id=session.id,
                opportunity_score=84,
                demand_level="high",
                competition_level="medium",
                profit_level="good",
                summary="Second writer.",
            ),
        )

        assert results[0].id == results[1].id

        count = await connection_a.fetchval(
            "SELECT count(*) FROM research_results WHERE research_session_id = $1", session.id
        )
        assert count == 1
    finally:
        await connection_a.execute("DELETE FROM projects WHERE id = $1", project.id)
        await connection_a.close()
        await connection_b.close()
