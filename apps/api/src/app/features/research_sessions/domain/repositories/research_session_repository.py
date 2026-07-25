from abc import ABC, abstractmethod
from uuid import UUID

from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSession,
    ResearchSessionStatus,
)


class ResearchSessionRepository(ABC):
    @abstractmethod
    async def create(self, project_id: UUID, marketplace: Marketplace) -> ResearchSession:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, research_session_id: UUID) -> ResearchSession | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_project_id(self, project_id: UUID) -> list[ResearchSession]:
        raise NotImplementedError

    @abstractmethod
    async def update_status(
        self, research_session_id: UUID, status: ResearchSessionStatus
    ) -> ResearchSession:
        raise NotImplementedError
