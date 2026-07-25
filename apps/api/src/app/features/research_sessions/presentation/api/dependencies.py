import asyncpg
from fastapi import Depends

from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.projects.presentation.api.dependencies import get_project_repository
from app.features.research_sessions.application.use_cases.create_research_session import (
    CreateResearchSessionUseCase,
)
from app.features.research_sessions.application.use_cases.list_research_sessions import (
    ListResearchSessionsForProjectUseCase,
)
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)
from app.features.research_sessions.infrastructure.database.repositories.postgres_research_session_repository import (  # noqa: E501
    PostgresResearchSessionRepository,
)
from app.infrastructure.database.connection import get_pool


async def get_research_session_repository(
    pool: asyncpg.Pool = Depends(get_pool),  # noqa: B008
) -> ResearchSessionRepository:
    return PostgresResearchSessionRepository(pool)


def get_create_research_session_use_case(
    project_repository: ProjectRepository = Depends(get_project_repository),  # noqa: B008
    research_session_repository: ResearchSessionRepository = Depends(  # noqa: B008
        get_research_session_repository
    ),
) -> CreateResearchSessionUseCase:
    return CreateResearchSessionUseCase(project_repository, research_session_repository)


def get_list_research_sessions_use_case(
    project_repository: ProjectRepository = Depends(get_project_repository),  # noqa: B008
    research_session_repository: ResearchSessionRepository = Depends(  # noqa: B008
        get_research_session_repository
    ),
) -> ListResearchSessionsForProjectUseCase:
    return ListResearchSessionsForProjectUseCase(project_repository, research_session_repository)
