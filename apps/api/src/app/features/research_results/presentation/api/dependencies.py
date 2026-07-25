import asyncpg
from fastapi import Depends

from app.features.research_results.application.use_cases.create_research_result import (
    CreateResearchResultUseCase,
)
from app.features.research_results.domain.repositories.research_result_repository import (
    ResearchResultRepository,
)
from app.features.research_results.infrastructure.database.repositories.postgres_research_result_repository import (  # noqa: E501
    PostgresResearchResultRepository,
)
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)
from app.features.research_sessions.presentation.api.dependencies import (
    get_research_session_repository,
)
from app.infrastructure.database.connection import get_pool


async def get_research_result_repository(
    pool: asyncpg.Pool = Depends(get_pool),  # noqa: B008
) -> ResearchResultRepository:
    return PostgresResearchResultRepository(pool)


def get_create_research_result_use_case(
    research_session_repository: ResearchSessionRepository = Depends(  # noqa: B008
        get_research_session_repository
    ),
    research_result_repository: ResearchResultRepository = Depends(  # noqa: B008
        get_research_result_repository
    ),
) -> CreateResearchResultUseCase:
    return CreateResearchResultUseCase(research_session_repository, research_result_repository)
