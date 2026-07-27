from uuid import UUID

from app.features.research_engine.domain.providers.insight_provider import InsightProvider
from app.features.research_engine.domain.providers.marketplace_data_provider import (
    MarketplaceDataProvider,
)
from app.features.research_results.domain.repositories.research_result_repository import (
    ResearchResultRepository,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSessionStatus,
)
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)


class RunResearchWorkerUseCase:
    """The Research Worker: runs a research session to completion.

    Transitions the session pending -> running -> completed, collecting
    findings via the marketplace provider registered for the session's
    marketplace and turning them into a stored result via the insight
    provider. On any failure the session is marked failed and the error is
    re-raised (logged by the global exception handler).
    """

    def __init__(
        self,
        research_session_repository: ResearchSessionRepository,
        research_result_repository: ResearchResultRepository,
        marketplace_data_providers: dict[Marketplace, MarketplaceDataProvider],
        insight_provider: InsightProvider,
    ) -> None:
        self._research_session_repository = research_session_repository
        self._research_result_repository = research_result_repository
        self._marketplace_data_providers = marketplace_data_providers
        self._insight_provider = insight_provider

    async def execute(self, research_session_id: UUID) -> None:
        session = await self._research_session_repository.get_by_id(research_session_id)
        if session is None:
            return

        try:
            await self._research_session_repository.update_status(
                session.id, ResearchSessionStatus.RUNNING
            )

            provider = self._marketplace_data_providers[session.marketplace]
            findings = await provider.collect(session)
            insights = await self._insight_provider.generate_insights(findings)

            await self._research_result_repository.create(
                research_session_id=session.id,
                opportunity_score=insights.opportunity_score,
                demand_level=insights.demand_level,
                competition_level=insights.competition_level,
                profit_level=insights.profit_level,
                summary=insights.summary,
            )

            await self._research_session_repository.update_status(
                session.id, ResearchSessionStatus.COMPLETED
            )
        except Exception:
            await self._research_session_repository.update_status(
                session.id, ResearchSessionStatus.FAILED
            )
            raise
