from uuid import uuid4

import pytest

from app.features.projects.application.dtos import GetProjectRequestDTO
from app.features.projects.application.use_cases.get_project import GetProjectUseCase
from app.features.projects.domain.exceptions import ProjectNotFoundError


async def test_execute_returns_existing_project(fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")
    use_case = GetProjectUseCase(fake_project_repository)

    result = await use_case.execute(GetProjectRequestDTO(project_id=project.id))

    assert result.id == project.id
    assert result.name == "Kitchen Research"


async def test_execute_raises_when_project_does_not_exist(fake_project_repository):
    use_case = GetProjectUseCase(fake_project_repository)

    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(GetProjectRequestDTO(project_id=uuid4()))
