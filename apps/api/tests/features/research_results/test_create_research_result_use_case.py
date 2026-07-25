from uuid import uuid4

import pytest

from app.features.research_results.application.dtos import CreateResearchResultRequestDTO
from app.features.research_results.application.use_cases.create_research_result import (
    CreateResearchResultUseCase,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSessionStatus,
)
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError


async def test_execute_creates_fake_result_when_none_exists(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    use_case = CreateResearchResultUseCase(
        fake_research_session_repository, fake_research_result_repository
    )

    result = await use_case.execute(CreateResearchResultRequestDTO(research_session_id=session.id))

    assert result.research_session_id == session.id
    assert result.opportunity_score == 84
    assert result.demand_level == "high"
    assert result.competition_level == "medium"
    assert result.profit_level == "good"
    assert result.summary == "This product shows promising demand with manageable competition."
    assert fake_research_result_repository.created == [session.id]


async def test_execute_returns_existing_result_without_creating_another(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    use_case = CreateResearchResultUseCase(
        fake_research_session_repository, fake_research_result_repository
    )

    first = await use_case.execute(CreateResearchResultRequestDTO(research_session_id=session.id))
    second = await use_case.execute(CreateResearchResultRequestDTO(research_session_id=session.id))

    assert first.id == second.id
    assert fake_research_result_repository.created == [session.id]


async def test_execute_marks_session_completed_after_generating_result(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    assert session.status == ResearchSessionStatus.PENDING
    use_case = CreateResearchResultUseCase(
        fake_research_session_repository, fake_research_result_repository
    )

    await use_case.execute(CreateResearchResultRequestDTO(research_session_id=session.id))

    updated_session = await fake_research_session_repository.get_by_id(session.id)
    assert updated_session.status == ResearchSessionStatus.COMPLETED


async def test_execute_raises_when_research_session_does_not_exist(
    fake_research_session_repository, fake_research_result_repository
):
    use_case = CreateResearchResultUseCase(
        fake_research_session_repository, fake_research_result_repository
    )

    with pytest.raises(ResearchSessionNotFoundError):
        await use_case.execute(CreateResearchResultRequestDTO(research_session_id=uuid4()))

    assert fake_research_result_repository.created == []
