from uuid import uuid4

import pytest

from app.features.research_results.application.dtos import GetResearchResultRequestDTO
from app.features.research_results.application.use_cases.get_research_result import (
    GetResearchResultUseCase,
)
from app.features.research_results.domain.exceptions import ResearchResultNotFoundError
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError


async def test_execute_returns_existing_result(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    await fake_research_result_repository.create(
        research_session_id=session.id,
        opportunity_score=84,
        demand_level="high",
        competition_level="medium",
        profit_level="good",
        summary="Looks promising.",
    )
    use_case = GetResearchResultUseCase(
        fake_research_session_repository, fake_research_result_repository
    )

    result = await use_case.execute(GetResearchResultRequestDTO(research_session_id=session.id))

    assert result.research_session_id == session.id
    assert result.opportunity_score == 84
    assert result.summary == "Looks promising."


async def test_execute_raises_when_result_is_not_ready_yet(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    use_case = GetResearchResultUseCase(
        fake_research_session_repository, fake_research_result_repository
    )

    with pytest.raises(ResearchResultNotFoundError):
        await use_case.execute(GetResearchResultRequestDTO(research_session_id=session.id))


async def test_execute_raises_when_research_session_does_not_exist(
    fake_research_session_repository, fake_research_result_repository
):
    use_case = GetResearchResultUseCase(
        fake_research_session_repository, fake_research_result_repository
    )

    with pytest.raises(ResearchSessionNotFoundError):
        await use_case.execute(GetResearchResultRequestDTO(research_session_id=uuid4()))
