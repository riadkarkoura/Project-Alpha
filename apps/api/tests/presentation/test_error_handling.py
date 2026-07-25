import pytest
from fastapi.testclient import TestClient

from app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from app.features.projects.presentation.api.dependencies import get_create_project_use_case
from app.main import app


class _ExplodingUseCase:
    async def execute(self, request: object) -> None:
        raise RuntimeError("boom")


@pytest.fixture
def client():
    def override_use_case() -> CreateProjectUseCase:
        return _ExplodingUseCase()  # type: ignore[return-value]

    app.dependency_overrides[get_create_project_use_case] = override_use_case
    yield TestClient(app, raise_server_exceptions=False)
    app.dependency_overrides.clear()


def test_unhandled_exception_returns_generic_500(client):
    response = client.post("/api/v1/projects", json={"name": "Kitchen Research"})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
