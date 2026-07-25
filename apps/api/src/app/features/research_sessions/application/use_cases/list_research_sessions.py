from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.research_sessions.application.dtos import (
    ListResearchSessionsRequestDTO,
    ResearchSessionDTO,
)
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)


class ListResearchSessionsForProjectUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        research_session_repository: ResearchSessionRepository,
    ) -> None:
        self._project_repository = project_repository
        self._research_session_repository = research_session_repository

    async def execute(self, request: ListResearchSessionsRequestDTO) -> list[ResearchSessionDTO]:
        project = await self._project_repository.get_by_id(request.project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {request.project_id} not found.")

        sessions = await self._research_session_repository.list_by_project_id(request.project_id)
        return [
            ResearchSessionDTO(
                id=session.id,
                project_id=session.project_id,
                marketplace=session.marketplace,
                status=session.status,
                created_at=session.created_at,
                updated_at=session.updated_at,
            )
            for session in sessions
        ]
