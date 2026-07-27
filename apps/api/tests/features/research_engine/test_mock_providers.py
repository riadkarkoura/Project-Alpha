from datetime import UTC, datetime
from uuid import uuid4

from app.features.research_engine.domain.entities.research_findings import RawResearchFindings
from app.features.research_engine.infrastructure.providers.mock_insight_provider import (
    MockInsightProvider,
)
from app.features.research_engine.infrastructure.providers.mock_marketplace_data_provider import (
    MockMarketplaceDataProvider,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSession,
    ResearchSessionStatus,
)


def _session(marketplace: Marketplace) -> ResearchSession:
    now = datetime.now(UTC)
    return ResearchSession(
        id=uuid4(),
        project_id=uuid4(),
        marketplace=marketplace,
        status=ResearchSessionStatus.PENDING,
        created_at=now,
        updated_at=now,
    )


async def test_marketplace_provider_is_deterministic_for_the_same_session():
    provider = MockMarketplaceDataProvider()
    session = _session(Marketplace.AMAZON)

    first = await provider.collect(session)
    second = await provider.collect(session)

    assert first == second


async def test_marketplace_provider_differs_across_sessions():
    provider = MockMarketplaceDataProvider()

    first = await provider.collect(_session(Marketplace.AMAZON))
    second = await provider.collect(_session(Marketplace.AMAZON))

    assert first != second


async def test_marketplace_provider_signals_are_within_expected_range():
    provider = MockMarketplaceDataProvider()

    findings = await provider.collect(_session(Marketplace.TIKTOK))

    assert 0 <= findings.demand_signal <= 100
    assert 0 <= findings.competition_signal <= 100
    assert 0 <= findings.profit_signal <= 100
    assert findings.marketplace == Marketplace.TIKTOK


async def test_insight_provider_is_deterministic_for_the_same_findings():
    provider = MockInsightProvider()
    findings = RawResearchFindings(
        marketplace=Marketplace.AMAZON, demand_signal=80, competition_signal=20, profit_signal=90
    )

    first = await provider.generate_insights(findings)
    second = await provider.generate_insights(findings)

    assert first == second
    assert 0 <= first.opportunity_score <= 100
