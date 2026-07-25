import asyncpg
from fastapi import Depends

from app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from app.features.projects.application.use_cases.get_project import GetProjectUseCase
from app.features.projects.application.use_cases.list_projects import ListProjectsUseCase
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


def get_list_projects_use_case(
    repository: ProjectRepository = Depends(get_project_repository),  # noqa: B008
) -> ListProjectsUseCase:
    return ListProjectsUseCase(repository)


def get_get_project_use_case(
    repository: ProjectRepository = Depends(get_project_repository),  # noqa: B008
) -> GetProjectUseCase:
    return GetProjectUseCase(repository)
