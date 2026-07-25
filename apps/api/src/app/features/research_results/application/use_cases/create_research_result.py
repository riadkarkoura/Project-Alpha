from app.features.research_results.application.dtos import (
    CreateResearchResultRequestDTO,
    ResearchResultResponseDTO,
)
from app.features.research_results.domain.repositories.research_result_repository import (
    ResearchResultRepository,
)
from app.features.research_sessions.domain.entities.research_session import (
    ResearchSessionStatus,
)
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)

# Placeholder values until a real analysis pipeline exists. This use case is the
# seam a future AI pipeline will replace: same interface, real inputs instead of
# these constants.
_FAKE_OPPORTUNITY_SCORE = 84
_FAKE_DEMAND_LEVEL = "high"
_FAKE_COMPETITION_LEVEL = "medium"
_FAKE_PROFIT_LEVEL = "good"
_FAKE_SUMMARY = "This product shows promising demand with manageable competition."


class CreateResearchResultUseCase:
    def __init__(
        self,
        research_session_repository: ResearchSessionRepository,
        research_result_repository: ResearchResultRepository,
    ) -> None:
        self._research_session_repository = research_session_repository
        self._research_result_repository = research_result_repository

    async def execute(self, request: CreateResearchResultRequestDTO) -> ResearchResultResponseDTO:
        session = await self._research_session_repository.get_by_id(request.research_session_id)
        if session is None:
            raise ResearchSessionNotFoundError(
                f"Research session {request.research_session_id} not found."
            )

        existing_result = await self._research_result_repository.get_by_research_session_id(
            request.research_session_id
        )
        result = existing_result or await self._research_result_repository.create(
            research_session_id=request.research_session_id,
            opportunity_score=_FAKE_OPPORTUNITY_SCORE,
            demand_level=_FAKE_DEMAND_LEVEL,
            competition_level=_FAKE_COMPETITION_LEVEL,
            profit_level=_FAKE_PROFIT_LEVEL,
            summary=_FAKE_SUMMARY,
        )

        if session.status != ResearchSessionStatus.COMPLETED:
            await self._research_session_repository.update_status(
                session.id, ResearchSessionStatus.COMPLETED
            )

        return ResearchResultResponseDTO(
            id=result.id,
            research_session_id=result.research_session_id,
            opportunity_score=result.opportunity_score,
            demand_level=result.demand_level,
            competition_level=result.competition_level,
            profit_level=result.profit_level,
            summary=result.summary,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )
