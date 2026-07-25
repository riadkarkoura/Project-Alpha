from uuid import uuid4

import pytest

from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.research_sessions.application.dtos import CreateResearchSessionRequestDTO
from app.features.research_sessions.application.use_cases.create_research_session import (
    CreateResearchSessionUseCase,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSessionStatus,
)


async def test_execute_creates_session_with_pending_status(
    fake_project_repository, fake_research_session_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    use_case = CreateResearchSessionUseCase(
        fake_project_repository, fake_research_session_repository
    )

    result = await use_case.execute(
        CreateResearchSessionRequestDTO(project_id=project.id, marketplace=Marketplace.AMAZON)
    )

    assert result.project_id == project.id
    assert result.marketplace == Marketplace.AMAZON
    assert result.status == ResearchSessionStatus.PENDING


async def test_execute_delegates_creation_to_repository(
    fake_project_repository, fake_research_session_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    use_case = CreateResearchSessionUseCase(
        fake_project_repository, fake_research_session_repository
    )

    await use_case.execute(
        CreateResearchSessionRequestDTO(project_id=project.id, marketplace=Marketplace.AMAZON)
    )

    assert fake_research_session_repository.created == [(project.id, Marketplace.AMAZON)]


async def test_execute_raises_when_project_does_not_exist(
    fake_project_repository, fake_research_session_repository
):
    use_case = CreateResearchSessionUseCase(
        fake_project_repository, fake_research_session_repository
    )

    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(
            CreateResearchSessionRequestDTO(project_id=uuid4(), marketplace=Marketplace.AMAZON)
        )

    assert fake_research_session_repository.created == []
