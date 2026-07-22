import pytest
from fastapi.testclient import TestClient

from app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from app.features.projects.presentation.api.dependencies import get_create_project_use_case
from app.main import app


@pytest.fixture
def client(fake_project_repository):
    def override_use_case() -> CreateProjectUseCase:
        return CreateProjectUseCase(fake_project_repository)

    app.dependency_overrides[get_create_project_use_case] = override_use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_project_returns_201_with_created_project(client):
    response = client.post("/api/v1/projects", json={"name": "Kitchen Research"})

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Kitchen Research"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_project_rejects_name_below_minimum_length(client):
    response = client.post("/api/v1/projects", json={"name": "ab"})

    assert response.status_code == 422


def test_create_project_rejects_whitespace_only_name(client):
    response = client.post("/api/v1/projects", json={"name": "   "})

    assert response.status_code == 422


def test_create_project_rejects_missing_name(client):
    response = client.post("/api/v1/projects", json={})

    assert response.status_code == 422
