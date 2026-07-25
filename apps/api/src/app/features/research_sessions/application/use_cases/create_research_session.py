from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.research_sessions.application.dtos import (
    CreateResearchSessionRequestDTO,
    ResearchSessionDTO,
)
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)


class CreateResearchSessionUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        research_session_repository: ResearchSessionRepository,
    ) -> None:
        self._project_repository = project_repository
        self._research_session_repository = research_session_repository

    async def execute(self, request: CreateResearchSessionRequestDTO) -> ResearchSessionDTO:
        project = await self._project_repository.get_by_id(request.project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {request.project_id} not found.")

        session = await self._research_session_repository.create(
            project_id=request.project_id, marketplace=request.marketplace
        )
        return ResearchSessionDTO(
            id=session.id,
            project_id=session.project_id,
            marketplace=session.marketplace,
            status=session.status,
            created_at=session.created_at,
            updated_at=session.updated_at,
        )
