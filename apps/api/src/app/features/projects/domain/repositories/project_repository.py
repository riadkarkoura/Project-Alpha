from abc import ABC, abstractmethod
from uuid import UUID

from app.features.projects.domain.entities.project import Project


class ProjectRepository(ABC):
    @abstractmethod
    async def create(self, name: str) -> Project:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, project_id: UUID) -> Project | None:
        raise NotImplementedError

    @abstractmethod
    async def list_all(self) -> list[Project]:
        raise NotImplementedError
