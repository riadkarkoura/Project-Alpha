from abc import ABC, abstractmethod

from app.features.research_engine.domain.entities.research_findings import RawResearchFindings
from app.features.research_sessions.domain.entities.research_session import ResearchSession


class MarketplaceDataProvider(ABC):
    """Port for a marketplace connector (Amazon, eBay, TikTok, ...).

    Implementations collect raw demand/competition/profit signals for a
    research session. A future real implementation calls out to the actual
    marketplace API; it must not change this contract.
    """

    @abstractmethod
    async def collect(self, session: ResearchSession) -> RawResearchFindings:
        raise NotImplementedError
