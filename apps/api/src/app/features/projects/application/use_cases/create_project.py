from app.features.projects.application.dtos import (
    CreateProjectRequestDTO,
    CreateProjectResponseDTO,
)
from app.features.projects.domain.exceptions import InvalidProjectNameError
from app.features.projects.domain.repositories.project_repository import ProjectRepository

MIN_NAME_LENGTH = 3
MAX_NAME_LENGTH = 100


class CreateProjectUseCase:
    def __init__(self, repository: ProjectRepository) -> None:
        self._repository = repository

    async def execute(self, request: CreateProjectRequestDTO) -> CreateProjectResponseDTO:
        name = self._validate_name(request.name)
        project = await self._repository.create(name)
        return CreateProjectResponseDTO(
            id=project.id,
            name=project.name,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    @staticmethod
    def _validate_name(name: str) -> str:
        trimmed = name.strip()
        if not trimmed:
            raise InvalidProjectNameError("Project name cannot be empty.")
        if len(trimmed) < MIN_NAME_LENGTH:
            raise InvalidProjectNameError(
                f"Project name must be at least {MIN_NAME_LENGTH} characters."
            )
        if len(trimmed) > MAX_NAME_LENGTH:
            raise InvalidProjectNameError(
                f"Project name must be at most {MAX_NAME_LENGTH} characters."
            )
        return trimmed
