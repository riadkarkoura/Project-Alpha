from app.features.projects.application.dtos import ProjectDTO
from app.features.projects.domain.repositories.project_repository import ProjectRepository


class ListProjectsUseCase:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    async def execute(self) -> list[ProjectDTO]:
        projects = await self._repository.list_all()
        return [
            ProjectDTO(
                id=project.id,
                name=project.name,
                created_at=project.created_at,
                updated_at=project.updated_at,
            )
            for project in projects
        ]
