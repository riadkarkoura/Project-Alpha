from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.features.projects.application.use_cases.get_project import GetProjectUseCase
from app.features.projects.application.use_cases.list_projects import ListProjectsUseCase
from app.features.projects.presentation.api.dependencies import (
    get_get_project_use_case,
    get_list_projects_use_case,
)
from app.main import app


@pytest.fixture
def client(fake_project_repository):
    def override_list_use_case() -> ListProjectsUseCase:
        return ListProjectsUseCase(fake_project_repository)

    def override_get_use_case() -> GetProjectUseCase:
        return GetProjectUseCase(fake_project_repository)

    app.dependency_overrides[get_list_projects_use_case] = override_list_use_case
    app.dependency_overrides[get_get_project_use_case] = override_get_use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_list_projects_returns_empty_list_when_none_exist(client):
    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    assert response.json() == []


async def test_list_projects_returns_created_projects(client, fake_project_repository):
    await fake_project_repository.create("Kitchen Research")

    response = client.get("/api/v1/projects")

    assert response.status_code == 200
    names = [project["name"] for project in response.json()]
    assert names == ["Kitchen Research"]


async def test_get_project_returns_existing_project(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.get(f"/api/v1/projects/{project.id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Kitchen Research"


def test_get_project_returns_404_for_unknown_project(client):
    response = client.get(f"/api/v1/projects/{uuid4()}")

    assert response.status_code == 404
