from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.features.research_sessions.application.use_cases.create_research_session import (
    CreateResearchSessionUseCase,
)
from app.features.research_sessions.presentation.api.dependencies import (
    get_create_research_session_use_case,
)
from app.main import app


@pytest.fixture
def client(fake_project_repository, fake_research_session_repository):
    def override_use_case() -> CreateResearchSessionUseCase:
        return CreateResearchSessionUseCase(
            fake_project_repository, fake_research_session_repository
        )

    app.dependency_overrides[get_create_research_session_use_case] = override_use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


async def test_create_research_session_returns_201_pending_session(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/research-sessions",
        json={"marketplace": "amazon"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == str(project.id)
    assert body["marketplace"] == "amazon"
    assert body["status"] == "pending"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


async def test_create_research_session_returns_404_for_unknown_project(client):
    response = client.post(
        f"/api/v1/projects/{uuid4()}/research-sessions",
        json={"marketplace": "amazon"},
    )

    assert response.status_code == 404


@pytest.mark.parametrize("marketplace", ["", "   ", "shopify", "Amazon"])
async def test_create_research_session_rejects_unsupported_marketplace(
    client, fake_project_repository, marketplace
):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/research-sessions",
        json={"marketplace": marketplace},
    )

    assert response.status_code == 422


async def test_create_research_session_rejects_missing_marketplace(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/research-sessions",
        json={},
    )

    assert response.status_code == 422


@pytest.mark.parametrize("marketplace", ["amazon", "ebay", "tiktok"])
async def test_create_research_session_accepts_all_supported_marketplaces(
    client, fake_project_repository, marketplace
):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/research-sessions",
        json={"marketplace": marketplace},
    )

    assert response.status_code == 201
    assert response.json()["marketplace"] == marketplace
