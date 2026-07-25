from uuid import UUID

import asyncpg

from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSession,
    ResearchSessionStatus,
)
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)

_INSERT_RESEARCH_SESSION_QUERY = """
    INSERT INTO research_sessions (project_id, marketplace)
    VALUES ($1, $2)
    RETURNING id, project_id, marketplace, status, created_at, updated_at
"""

_SELECT_RESEARCH_SESSION_BY_ID_QUERY = """
    SELECT id, project_id, marketplace, status, created_at, updated_at
    FROM research_sessions
    WHERE id = $1
"""

_SELECT_RESEARCH_SESSIONS_BY_PROJECT_ID_QUERY = """
    SELECT id, project_id, marketplace, status, created_at, updated_at
    FROM research_sessions
    WHERE project_id = $1
    ORDER BY created_at DESC
"""

_UPDATE_RESEARCH_SESSION_STATUS_QUERY = """
    UPDATE research_sessions
    SET status = $2
    WHERE id = $1
    RETURNING id, project_id, marketplace, status, created_at, updated_at
"""


class PostgresResearchSessionRepository(ResearchSessionRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(self, project_id: UUID, marketplace: Marketplace) -> ResearchSession:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                _INSERT_RESEARCH_SESSION_QUERY, project_id, marketplace.value
            )

        return self._to_entity(row)

    async def get_by_id(self, research_session_id: UUID) -> ResearchSession | None:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                _SELECT_RESEARCH_SESSION_BY_ID_QUERY, research_session_id
            )

        if row is None:
            return None

        return self._to_entity(row)

    async def list_by_project_id(self, project_id: UUID) -> list[ResearchSession]:
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(
                _SELECT_RESEARCH_SESSIONS_BY_PROJECT_ID_QUERY, project_id
            )

        return [self._to_entity(row) for row in rows]

    async def update_status(
        self, research_session_id: UUID, status: ResearchSessionStatus
    ) -> ResearchSession:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                _UPDATE_RESEARCH_SESSION_STATUS_QUERY, research_session_id, status.value
            )

        if row is None:
            raise ValueError(f"Research session {research_session_id} not found.")

        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> ResearchSession:
        return ResearchSession(
            id=row["id"],
            project_id=row["project_id"],
            marketplace=Marketplace(row["marketplace"]),
            status=ResearchSessionStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
