from app.features.research_results.application.dtos import (
    GetResearchResultRequestDTO,
    ResearchResultResponseDTO,
)
from app.features.research_results.domain.exceptions import ResearchResultNotFoundError
from app.features.research_results.domain.repositories.research_result_repository import (
    ResearchResultRepository,
)
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)


class GetResearchResultUseCase:
    def __init__(
        self,
        research_session_repository: ResearchSessionRepository,
        research_result_repository: ResearchResultRepository,
    ) -> None:
        self._research_session_repository = research_session_repository
        self._research_result_repository = research_result_repository

    async def execute(self, request: GetResearchResultRequestDTO) -> ResearchResultResponseDTO:
        session = await self._research_session_repository.get_by_id(request.research_session_id)
        if session is None:
            raise ResearchSessionNotFoundError(
                f"Research session {request.research_session_id} not found."
            )

        result = await self._research_result_repository.get_by_research_session_id(
            request.research_session_id
        )
        if result is None:
            raise ResearchResultNotFoundError(
                f"Research result for session {request.research_session_id} is not ready yet."
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
