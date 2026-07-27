from app.features.research_engine.domain.entities.research_findings import (
    RawResearchFindings,
    ResearchInsights,
)
from app.features.research_engine.domain.providers.insight_provider import InsightProvider

_HIGH_THRESHOLD = 70
_MEDIUM_THRESHOLD = 40


def _level(signal: int) -> str:
    if signal >= _HIGH_THRESHOLD:
        return "high"
    if signal >= _MEDIUM_THRESHOLD:
        return "medium"
    return "low"


def _profit_level(signal: int) -> str:
    if signal >= _HIGH_THRESHOLD:
        return "good"
    if signal >= _MEDIUM_THRESHOLD:
        return "fair"
    return "poor"


class MockInsightProvider(InsightProvider):
    """Deterministic stand-in for a real LLM analysis provider.

    Turns raw signals into a score and narrative summary using fixed rules -
    no external calls, no randomness.
    """

    async def generate_insights(self, findings: RawResearchFindings) -> ResearchInsights:
        opportunity_score = round(
            (findings.demand_signal + findings.profit_signal + (100 - findings.competition_signal))
            / 3
        )
        demand_level = _level(findings.demand_signal)
        competition_level = _level(findings.competition_signal)
        profit_level = _profit_level(findings.profit_signal)
        summary = (
            f"{findings.marketplace.value.title()} shows {demand_level} demand, "
            f"{competition_level} competition, and {profit_level} profit potential "
            f"(opportunity score {opportunity_score}/100)."
        )

        return ResearchInsights(
            opportunity_score=opportunity_score,
            demand_level=demand_level,
            competition_level=competition_level,
            profit_level=profit_level,
            summary=summary,
        )
