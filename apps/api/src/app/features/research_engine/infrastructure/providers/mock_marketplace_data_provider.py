import hashlib
import random

from app.features.research_engine.domain.entities.research_findings import RawResearchFindings
from app.features.research_engine.domain.providers.marketplace_data_provider import (
    MarketplaceDataProvider,
)
from app.features.research_sessions.domain.entities.research_session import ResearchSession


def _seed_for(session: ResearchSession) -> int:
    digest = hashlib.sha256(str(session.id).encode()).digest()
    return int.from_bytes(digest[:8], byteorder="big")


class MockMarketplaceDataProvider(MarketplaceDataProvider):
    """Deterministic stand-in for a real marketplace connector.

    Signals are derived from a hash of the session id, so the same session
    always produces the same findings - no external calls, no randomness
    across runs.
    """

    async def collect(self, session: ResearchSession) -> RawResearchFindings:
        rng = random.Random(_seed_for(session))
        return RawResearchFindings(
            marketplace=session.marketplace,
            demand_signal=rng.randint(30, 100),
            competition_signal=rng.randint(10, 90),
            profit_signal=rng.randint(30, 100),
        )
