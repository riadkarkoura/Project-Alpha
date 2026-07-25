from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.features.research_sessions.application.use_cases.list_research_sessions import (
    ListResearchSessionsForProjectUseCase,
)
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.features.research_sessions.presentation.api.dependencies import (
    get_list_research_sessions_use_case,
)
from app.main import app


@pytest.fixture
def client(fake_project_repository, fake_research_session_repository):
    def override_use_case() -> ListResearchSessionsForProjectUseCase:
        return ListResearchSessionsForProjectUseCase(
            fake_project_repository, fake_research_session_repository
        )

    app.dependency_overrides[get_list_research_sessions_use_case] = override_use_case
    yield TestClient(app)
    app.dependency_overrides.clear()


async def test_list_research_sessions_returns_sessions_for_project(
    client, fake_project_repository, fake_research_session_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    await fake_research_session_repository.create(project.id, Marketplace.AMAZON)

    response = client.get(f"/api/v1/projects/{project.id}/research-sessions")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["marketplace"] == "amazon"


def test_list_research_sessions_returns_404_for_unknown_project(client):
    response = client.get(f"/api/v1/projects/{uuid4()}/research-sessions")

    assert response.status_code == 404
