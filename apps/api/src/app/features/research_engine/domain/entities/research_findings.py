from dataclasses import dataclass

from app.features.research_sessions.domain.entities.research_session import Marketplace


@dataclass(frozen=True)
class RawResearchFindings:
    """Output of a MarketplaceDataProvider - normalized signals, not yet scored or narrated."""

    marketplace: Marketplace
    demand_signal: int
    competition_signal: int
    profit_signal: int


@dataclass(frozen=True)
class ResearchInsights:
    """Output of an InsightProvider - the scored, human-readable analysis of RawResearchFindings."""

    opportunity_score: int
    demand_level: str
    competition_level: str
    profit_level: str
    summary: str
