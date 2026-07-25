from uuid import uuid4

import pytest

from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.research_sessions.application.dtos import ListResearchSessionsRequestDTO
from app.features.research_sessions.application.use_cases.list_research_sessions import (
    ListResearchSessionsForProjectUseCase,
)
from app.features.research_sessions.domain.entities.research_session import Marketplace


async def test_execute_returns_sessions_for_project(
    fake_project_repository, fake_research_session_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    other_project = await fake_project_repository.create("Garage Research")
    await fake_research_session_repository.create(project.id, Marketplace.AMAZON)
    await fake_research_session_repository.create(project.id, Marketplace.EBAY)
    await fake_research_session_repository.create(other_project.id, Marketplace.TIKTOK)
    use_case = ListResearchSessionsForProjectUseCase(
        fake_project_repository, fake_research_session_repository
    )

    result = await use_case.execute(ListResearchSessionsRequestDTO(project_id=project.id))

    assert {session.marketplace for session in result} == {Marketplace.AMAZON, Marketplace.EBAY}


async def test_execute_raises_when_project_does_not_exist(
    fake_project_repository, fake_research_session_repository
):
    use_case = ListResearchSessionsForProjectUseCase(
        fake_project_repository, fake_research_session_repository
    )

    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(ListResearchSessionsRequestDTO(project_id=uuid4()))
