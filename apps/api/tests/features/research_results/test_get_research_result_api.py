from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.features.research_results.application.use_cases.get_research_result import (
    GetResearchResultUseCase,
)
from app.features.research_results.presentation.api.dependencies import (
    get_get_research_result_use_case,
)
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.main import app


@pytest.fixture
def client(fake_research_session_repository, fake_research_result_repository):
    def override_use_case() -> GetResearchResultUseCase:
        return GetResearchResultUseCase(
            fake_research_session_repository, fake_research_result_repository
        )

    app.dependency_overrides[get_get_research_result_use_case] = override_use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


async def test_get_research_result_returns_stored_result(
    client, fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    await fake_research_result_repository.create(
        research_session_id=session.id,
        opportunity_score=84,
        demand_level="high",
        competition_level="medium",
        profit_level="good",
        summary="Looks promising.",
    )

    response = client.get(f"/api/v1/research-sessions/{session.id}/research-result")

    assert response.status_code == 200
    body = response.json()
    assert body["research_session_id"] == str(session.id)
    assert body["opportunity_score"] == 84
    assert body["summary"] == "Looks promising."
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


async def test_get_research_result_returns_404_when_not_ready_yet(
    client, fake_research_session_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)

    response = client.get(f"/api/v1/research-sessions/{session.id}/research-result")

    assert response.status_code == 404


async def test_get_research_result_does_not_create_a_result_as_a_side_effect(
    client, fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)

    client.get(f"/api/v1/research-sessions/{session.id}/research-result")

    assert fake_research_result_repository.created == []


async def test_get_research_result_returns_404_for_unknown_research_session(client):
    response = client.get(f"/api/v1/research-sessions/{uuid4()}/research-result")

    assert response.status_code == 404
