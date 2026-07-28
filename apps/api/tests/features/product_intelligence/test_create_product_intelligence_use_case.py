from uuid import uuid4

import pytest

from app.features.product_intelligence.application.dtos import CreateProductIntelligenceRequestDTO
from app.features.product_intelligence.application.use_cases.create_product_intelligence import (
    CreateProductIntelligenceUseCase,
)
from app.features.product_intelligence.domain.exceptions import InvalidProductIntelligenceError
from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError


@pytest.fixture
def use_case(
    fake_product_intelligence_repository, fake_project_repository, fake_research_session_repository
):
    return CreateProductIntelligenceUseCase(
        fake_product_intelligence_repository,
        fake_project_repository,
        fake_research_session_repository,
    )


async def test_execute_creates_a_draft_product(use_case, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    result = await use_case.execute(
        CreateProductIntelligenceRequestDTO(
            project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
        )
    )

    assert result.project_id == project.id
    assert result.title == "Bamboo Cutting Board"
    assert result.status.value == "draft"


async def test_execute_trims_whitespace_from_title(use_case, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    result = await use_case.execute(
        CreateProductIntelligenceRequestDTO(
            project_id=project.id, research_session_id=None, title="  Bamboo Cutting Board  "
        )
    )

    assert result.title == "Bamboo Cutting Board"


@pytest.mark.parametrize("title", ["", "  ", "ab", "a" * 201])
async def test_execute_rejects_invalid_titles(use_case, fake_project_repository, title):
    project = await fake_project_repository.create("Kitchen Research")

    with pytest.raises(InvalidProductIntelligenceError):
        await use_case.execute(
            CreateProductIntelligenceRequestDTO(
                project_id=project.id, research_session_id=None, title=title
            )
        )


async def test_execute_raises_when_project_does_not_exist(use_case):
    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(
            CreateProductIntelligenceRequestDTO(
                project_id=uuid4(), research_session_id=None, title="Bamboo Cutting Board"
            )
        )


async def test_execute_links_a_valid_research_session(
    use_case, fake_project_repository, fake_research_session_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    session = await fake_research_session_repository.create(project.id, Marketplace.AMAZON)

    result = await use_case.execute(
        CreateProductIntelligenceRequestDTO(
            project_id=project.id, research_session_id=session.id, title="Bamboo Cutting Board"
        )
    )

    assert result.research_session_id == session.id


async def test_execute_raises_when_research_session_does_not_exist(
    use_case, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")

    with pytest.raises(ResearchSessionNotFoundError):
        await use_case.execute(
            CreateProductIntelligenceRequestDTO(
                project_id=project.id, research_session_id=uuid4(), title="Bamboo Cutting Board"
            )
        )


async def test_execute_raises_when_research_session_belongs_to_a_different_project(
    use_case, fake_project_repository, fake_research_session_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    other_project = await fake_project_repository.create("Garage Research")
    session = await fake_research_session_repository.create(other_project.id, Marketplace.AMAZON)

    with pytest.raises(InvalidProductIntelligenceError, match="does not belong"):
        await use_case.execute(
            CreateProductIntelligenceRequestDTO(
                project_id=project.id, research_session_id=session.id, title="Bamboo Cutting Board"
            )
        )
