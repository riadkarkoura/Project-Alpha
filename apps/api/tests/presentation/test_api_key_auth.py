from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.security import verify_api_key
from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.projects.presentation.api.dependencies import get_project_repository
from app.main import app


def test_request_without_api_key_is_rejected():
    app.dependency_overrides.pop(verify_api_key, None)
    client = TestClient(app)

    response = client.get("/api/v1/projects")

    assert response.status_code == 401


def test_request_with_wrong_api_key_is_rejected():
    app.dependency_overrides.pop(verify_api_key, None)
    client = TestClient(app)

    response = client.get("/api/v1/projects", headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401


def test_request_with_correct_api_key_is_accepted(fake_project_repository):
    app.dependency_overrides.pop(verify_api_key, None)

    def override_repository() -> ProjectRepository:
        return fake_project_repository

    app.dependency_overrides[get_project_repository] = override_repository
    client = TestClient(app)

    response = client.get("/api/v1/projects", headers={"X-API-Key": settings.api_key})

    assert response.status_code == 200
    app.dependency_overrides.pop(get_project_repository, None)


def test_health_check_does_not_require_api_key():
    app.dependency_overrides.pop(verify_api_key, None)
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
