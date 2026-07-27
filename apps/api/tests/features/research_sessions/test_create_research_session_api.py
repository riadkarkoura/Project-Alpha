from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.features.research_engine.application.use_cases.run_research_worker import (
    RunResearchWorkerUseCase,
)
from app.features.research_engine.infrastructure.providers.mock_insight_provider import (
    MockInsightProvider,
)
from app.features.research_engine.infrastructure.providers.mock_marketplace_data_provider import (
    MockMarketplaceDataProvider,
)
from app.features.research_engine.presentation.dependencies import (
    get_run_research_worker_use_case,
)
from app.features.research_sessions.application.use_cases.create_research_session import (
    CreateResearchSessionUseCase,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSessionStatus,
)
from app.features.research_sessions.presentation.api.dependencies import (
    get_create_research_session_use_case,
)
from app.main import app


@pytest.fixture
def client(
    fake_project_repository, fake_research_session_repository, fake_research_result_repository
):
    def override_use_case() -> CreateResearchSessionUseCase:
        return CreateResearchSessionUseCase(
            fake_project_repository, fake_research_session_repository
        )

    def override_worker_use_case() -> RunResearchWorkerUseCase:
        return RunResearchWorkerUseCase(
            fake_research_session_repository,
            fake_research_result_repository,
            dict.fromkeys(Marketplace, MockMarketplaceDataProvider()),
            MockInsightProvider(),
        )

    app.dependency_overrides[get_create_research_session_use_case] = override_use_case
    app.dependency_overrides[get_run_research_worker_use_case] = override_worker_use_case
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


async def test_create_research_session_triggers_worker_that_completes_it(
    client,
    fake_project_repository,
    fake_research_session_repository,
    fake_research_result_repository,
):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/research-sessions",
        json={"marketplace": "amazon"},
    )

    session_id = UUID(response.json()["id"])
    session = await fake_research_session_repository.get_by_id(session_id)
    assert session.status == ResearchSessionStatus.COMPLETED

    result = await fake_research_result_repository.get_by_research_session_id(session_id)
    assert result is not None


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
