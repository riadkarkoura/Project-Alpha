from app.features.projects.application.dtos import GetProjectRequestDTO, ProjectDTO
from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.projects.domain.repositories.project_repository import ProjectRepository


class GetProjectUseCase:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    async def execute(self, request: GetProjectRequestDTO) -> ProjectDTO:
        project = await self._repository.get_by_id(request.project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {request.project_id} not found.")

        return ProjectDTO(
            id=project.id,
            name=project.name,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
