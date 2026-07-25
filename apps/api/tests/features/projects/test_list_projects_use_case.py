from app.features.projects.application.use_cases.list_projects import ListProjectsUseCase


async def test_execute_returns_empty_list_when_no_projects_exist(fake_project_repository):
    use_case = ListProjectsUseCase(fake_project_repository)

    result = await use_case.execute()

    assert result == []


async def test_execute_returns_all_created_projects(fake_project_repository):
    await fake_project_repository.create("Kitchen Research")
    await fake_project_repository.create("Garage Research")
    use_case = ListProjectsUseCase(fake_project_repository)

    result = await use_case.execute()

    assert {project.name for project in result} == {"Kitchen Research", "Garage Research"}
