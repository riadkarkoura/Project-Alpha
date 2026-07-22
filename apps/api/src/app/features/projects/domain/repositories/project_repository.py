from abc import ABC, abstractmethod

from app.features.projects.domain.entities.project import Project


class ProjectRepository(ABC):
    @abstractmethod
    async def create(self, name: str) -> Project:
        raise NotImplementedError
