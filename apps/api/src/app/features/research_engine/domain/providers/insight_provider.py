from abc import ABC, abstractmethod

from app.features.research_engine.domain.entities.research_findings import (
    RawResearchFindings,
    ResearchInsights,
)


class InsightProvider(ABC):
    """Port for an AI analysis provider (OpenAI, Anthropic, ...).

    Implementations turn raw marketplace findings into a scored, narrated
    insight. A future real implementation calls out to an LLM; it must not
    change this contract.
    """

    @abstractmethod
    async def generate_insights(self, findings: RawResearchFindings) -> ResearchInsights:
        raise NotImplementedError
