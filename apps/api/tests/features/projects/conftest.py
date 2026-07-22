from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.features.projects.domain.entities.project import Project
from app.features.projects.domain.repositories.project_repository import ProjectRepository


class FakeProjectRepository(ProjectRepository):
    def __init__(self) -> None:
        self.created_names: list[str] = []

    async def create(self, name: str) -> Project:
        self.created_names.append(name)
        now = datetime.now(UTC)
        return Project(id=uuid4(), name=name, created_at=now, updated_at=now)


@pytest.fixture
def fake_project_repository() -> FakeProjectRepository:
    return FakeProjectRepository()
