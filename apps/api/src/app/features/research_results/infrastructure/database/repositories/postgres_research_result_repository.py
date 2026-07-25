from uuid import UUID

import asyncpg

from app.features.research_results.domain.entities.research_result import ResearchResult
from app.features.research_results.domain.repositories.research_result_repository import (
    ResearchResultRepository,
)

_INSERT_RESEARCH_RESULT_QUERY = """
    INSERT INTO research_results (
        research_session_id, opportunity_score, demand_level, competition_level,
        profit_level, summary
    )
    VALUES ($1, $2, $3, $4, $5, $6)
    ON CONFLICT (research_session_id) DO NOTHING
    RETURNING
        id, research_session_id, opportunity_score, demand_level, competition_level,
        profit_level, summary, created_at, updated_at
"""

_SELECT_BY_RESEARCH_SESSION_ID_QUERY = """
    SELECT
        id, research_session_id, opportunity_score, demand_level, competition_level,
        profit_level, summary, created_at, updated_at
    FROM research_results
    WHERE research_session_id = $1
"""


class PostgresResearchResultRepository(ResearchResultRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self,
        research_session_id: UUID,
        opportunity_score: int,
        demand_level: str,
        competition_level: str,
        profit_level: str,
        summary: str,
    ) -> ResearchResult:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                _INSERT_RESEARCH_RESULT_QUERY,
                research_session_id,
                opportunity_score,
                demand_level,
                competition_level,
                profit_level,
                summary,
            )

            if row is None:
                # Another request won the race and inserted the result first (the unique
                # constraint on research_session_id caused ON CONFLICT DO NOTHING to no-op).
                # Fetch what the winner committed instead of failing this request.
                row = await connection.fetchrow(
                    _SELECT_BY_RESEARCH_SESSION_ID_QUERY, research_session_id
                )

        if row is None:
            raise RuntimeError(
                f"Failed to create or fetch research result for session {research_session_id}."
            )

        return self._to_entity(row)

    async def get_by_research_session_id(self, research_session_id: UUID) -> ResearchResult | None:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                _SELECT_BY_RESEARCH_SESSION_ID_QUERY, research_session_id
            )

        if row is None:
            return None

        return self._to_entity(row)

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> ResearchResult:
        return ResearchResult(
            id=row["id"],
            research_session_id=row["research_session_id"],
            opportunity_score=row["opportunity_score"],
            demand_level=row["demand_level"],
            competition_level=row["competition_level"],
            profit_level=row["profit_level"],
            summary=row["summary"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
