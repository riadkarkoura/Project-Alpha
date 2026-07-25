from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.features.research_results.application.use_cases.create_research_result import (
    CreateResearchResultUseCase,
)
from app.features.research_results.presentation.api.dependencies import (
    get_create_research_result_use_case,
)
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.main import app


@pytest.fixture
def client(fake_research_session_repository, fake_research_result_repository):
    def override_use_case() -> CreateResearchResultUseCase:
        return CreateResearchResultUseCase(
            fake_research_session_repository, fake_research_result_repository
        )

    app.dependency_overrides[get_create_research_result_use_case] = override_use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


async def test_get_research_result_creates_fake_result_on_first_request(
    client, fake_research_session_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)

    response = client.get(f"/api/v1/research-sessions/{session.id}/research-result")

    assert response.status_code == 200
    body = response.json()
    assert body["research_session_id"] == str(session.id)
    assert body["opportunity_score"] == 84
    assert body["demand_level"] == "high"
    assert body["competition_level"] == "medium"
    assert body["profit_level"] == "good"
    assert body["summary"] == "This product shows promising demand with manageable competition."
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


async def test_get_research_result_returns_same_result_on_repeat_requests(
    client, fake_research_session_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)

    first = client.get(f"/api/v1/research-sessions/{session.id}/research-result")
    second = client.get(f"/api/v1/research-sessions/{session.id}/research-result")

    assert first.json()["id"] == second.json()["id"]


async def test_get_research_result_returns_404_for_unknown_research_session(client):
    response = client.get(f"/api/v1/research-sessions/{uuid4()}/research-result")

    assert response.status_code == 404
