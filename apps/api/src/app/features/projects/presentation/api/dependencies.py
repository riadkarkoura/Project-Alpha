import asyncpg
from fastapi import Depends

from app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.projects.infrastructure.database.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from app.infrastructure.database.connection import get_pool


async def get_project_repository(
    pool: asyncpg.Pool = Depends(get_pool),  # noqa: B008
) -> ProjectRepository:
    return PostgresProjectRepository(pool)


def get_create_project_use_case(
    repository: ProjectRepository = Depends(get_project_repository),  # noqa: B008
) -> CreateProjectUseCase:
    return CreateProjectUseCase(repository)
