import pytest

from app.features.projects.application.dtos import CreateProjectRequestDTO
from app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from app.features.projects.domain.exceptions import InvalidProjectNameError


async def test_execute_returns_project_with_given_name(fake_project_repository):
    use_case = CreateProjectUseCase(fake_project_repository)

    result = await use_case.execute(CreateProjectRequestDTO(name="Kitchen Research"))

    assert result.name == "Kitchen Research"
    assert result.id is not None
    assert result.created_at == result.updated_at


async def test_execute_delegates_creation_to_repository(fake_project_repository):
    use_case = CreateProjectUseCase(fake_project_repository)

    await use_case.execute(CreateProjectRequestDTO(name="Kitchen Research"))

    assert fake_project_repository.created_names == ["Kitchen Research"]


async def test_execute_trims_whitespace_before_creating(fake_project_repository):
    use_case = CreateProjectUseCase(fake_project_repository)

    result = await use_case.execute(CreateProjectRequestDTO(name="  Kitchen Research  "))

    assert result.name == "Kitchen Research"
    assert fake_project_repository.created_names == ["Kitchen Research"]


@pytest.mark.parametrize("name", ["", "   ", "ab", "a" * 101])
async def test_execute_rejects_invalid_names(fake_project_repository, name):
    use_case = CreateProjectUseCase(fake_project_repository)

    with pytest.raises(InvalidProjectNameError):
        await use_case.execute(CreateProjectRequestDTO(name=name))

    assert fake_project_repository.created_names == []
