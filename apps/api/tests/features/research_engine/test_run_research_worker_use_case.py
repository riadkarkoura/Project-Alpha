from uuid import uuid4

import pytest

from app.features.research_engine.application.use_cases.run_research_worker import (
    RunResearchWorkerUseCase,
)
from app.features.research_engine.domain.entities.research_findings import (
    RawResearchFindings,
    ResearchInsights,
)
from app.features.research_engine.domain.providers.insight_provider import InsightProvider
from app.features.research_engine.domain.providers.marketplace_data_provider import (
    MarketplaceDataProvider,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSession,
    ResearchSessionStatus,
)

_FINDINGS = RawResearchFindings(
    marketplace=Marketplace.AMAZON, demand_signal=80, competition_signal=20, profit_signal=90
)
_INSIGHTS = ResearchInsights(
    opportunity_score=84,
    demand_level="high",
    competition_level="low",
    profit_level="good",
    summary="Looks promising.",
)


class _FakeMarketplaceDataProvider(MarketplaceDataProvider):
    def __init__(self, findings: RawResearchFindings | None = None, error: Exception | None = None):
        self._findings = findings
        self._error = error
        self.calls: list[ResearchSession] = []

    async def collect(self, session: ResearchSession) -> RawResearchFindings:
        self.calls.append(session)
        if self._error is not None:
            raise self._error
        assert self._findings is not None
        return self._findings


class _FakeInsightProvider(InsightProvider):
    def __init__(self, insights: ResearchInsights | None = None, error: Exception | None = None):
        self._insights = insights
        self._error = error
        self.calls: list[RawResearchFindings] = []

    async def generate_insights(self, findings: RawResearchFindings) -> ResearchInsights:
        self.calls.append(findings)
        if self._error is not None:
            raise self._error
        assert self._insights is not None
        return self._insights


def _make_use_case(
    fake_research_session_repository,
    fake_research_result_repository,
    marketplace_provider: MarketplaceDataProvider,
    insight_provider: InsightProvider,
) -> RunResearchWorkerUseCase:
    return RunResearchWorkerUseCase(
        fake_research_session_repository,
        fake_research_result_repository,
        {marketplace: marketplace_provider for marketplace in Marketplace},
        insight_provider,
    )


async def test_execute_runs_session_to_completion_and_stores_result(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    marketplace_provider = _FakeMarketplaceDataProvider(findings=_FINDINGS)
    insight_provider = _FakeInsightProvider(insights=_INSIGHTS)
    use_case = _make_use_case(
        fake_research_session_repository,
        fake_research_result_repository,
        marketplace_provider,
        insight_provider,
    )

    await use_case.execute(session.id)

    updated_session = await fake_research_session_repository.get_by_id(session.id)
    assert updated_session.status == ResearchSessionStatus.COMPLETED

    result = await fake_research_result_repository.get_by_research_session_id(session.id)
    assert result is not None
    assert result.opportunity_score == 84
    assert result.summary == "Looks promising."

    assert marketplace_provider.calls == [session]
    assert insight_provider.calls == [_FINDINGS]


async def test_execute_marks_session_failed_when_provider_raises(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.AMAZON)
    marketplace_provider = _FakeMarketplaceDataProvider(error=RuntimeError("provider is down"))
    insight_provider = _FakeInsightProvider(insights=_INSIGHTS)
    use_case = _make_use_case(
        fake_research_session_repository,
        fake_research_result_repository,
        marketplace_provider,
        insight_provider,
    )

    with pytest.raises(RuntimeError):
        await use_case.execute(session.id)

    updated_session = await fake_research_session_repository.get_by_id(session.id)
    assert updated_session.status == ResearchSessionStatus.FAILED
    assert await fake_research_result_repository.get_by_research_session_id(session.id) is None


async def test_execute_does_nothing_when_session_does_not_exist(
    fake_research_session_repository, fake_research_result_repository
):
    marketplace_provider = _FakeMarketplaceDataProvider(findings=_FINDINGS)
    insight_provider = _FakeInsightProvider(insights=_INSIGHTS)
    use_case = _make_use_case(
        fake_research_session_repository,
        fake_research_result_repository,
        marketplace_provider,
        insight_provider,
    )

    await use_case.execute(uuid4())

    assert marketplace_provider.calls == []
    assert insight_provider.calls == []


async def test_execute_uses_the_provider_registered_for_the_session_marketplace(
    fake_research_session_repository, fake_research_result_repository
):
    session = await fake_research_session_repository.create(uuid4(), Marketplace.EBAY)
    amazon_provider = _FakeMarketplaceDataProvider(findings=_FINDINGS)
    ebay_provider = _FakeMarketplaceDataProvider(findings=_FINDINGS)
    insight_provider = _FakeInsightProvider(insights=_INSIGHTS)
    use_case = RunResearchWorkerUseCase(
        fake_research_session_repository,
        fake_research_result_repository,
        {Marketplace.AMAZON: amazon_provider, Marketplace.EBAY: ebay_provider},
        insight_provider,
    )

    await use_case.execute(session.id)

    assert ebay_provider.calls == [session]
    assert amazon_provider.calls == []
