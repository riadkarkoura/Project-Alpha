from uuid import UUID

import asyncpg

from app.features.projects.domain.entities.project import Project
from app.features.projects.domain.repositories.project_repository import ProjectRepository

_INSERT_PROJECT_QUERY = """
    INSERT INTO projects (name)
    VALUES ($1)
    RETURNING id, name, created_at, updated_at
"""

_SELECT_PROJECT_BY_ID_QUERY = """
    SELECT id, name, created_at, updated_at
    FROM projects
    WHERE id = $1
"""

_SELECT_ALL_PROJECTS_QUERY = """
    SELECT id, name, created_at, updated_at
    FROM projects
    ORDER BY created_at DESC
"""


class PostgresProjectRepository(ProjectRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(self, name: str) -> Project:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(_INSERT_PROJECT_QUERY, name)

        return self._to_entity(row)

    async def get_by_id(self, project_id: UUID) -> Project | None:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(_SELECT_PROJECT_BY_ID_QUERY, project_id)

        if row is None:
            return None

        return self._to_entity(row)

    async def list_all(self) -> list[Project]:
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(_SELECT_ALL_PROJECTS_QUERY)

        return [self._to_entity(row) for row in rows]

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> Project:
        return Project(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
