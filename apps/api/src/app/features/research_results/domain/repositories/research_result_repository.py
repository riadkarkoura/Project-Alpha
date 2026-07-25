from abc import ABC, abstractmethod
from uuid import UUID

from app.features.research_results.domain.entities.research_result import ResearchResult


class ResearchResultRepository(ABC):
    @abstractmethod
    async def create(
        self,
        research_session_id: UUID,
        opportunity_score: int,
        demand_level: str,
        competition_level: str,
        profit_level: str,
        summary: str,
    ) -> ResearchResult:
        raise NotImplementedError

    @abstractmethod
    async def get_by_research_session_id(self, research_session_id: UUID) -> ResearchResult | None:
        raise NotImplementedError
