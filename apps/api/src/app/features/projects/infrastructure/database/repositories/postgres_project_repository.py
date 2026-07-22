import asyncpg

from app.features.projects.domain.entities.project import Project
from app.features.projects.domain.repositories.project_repository import ProjectRepository

_INSERT_PROJECT_QUERY = """
    INSERT INTO projects (name)
    VALUES ($1)
    RETURNING id, name, created_at, updated_at
"""


class PostgresProjectRepository(ProjectRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(self, name: str) -> Project:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(_INSERT_PROJECT_QUERY, name)

        return Project(
            id=row["id"],
            name=row["name"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
