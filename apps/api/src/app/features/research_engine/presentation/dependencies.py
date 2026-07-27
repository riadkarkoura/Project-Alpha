from fastapi import Depends

from app.features.research_engine.application.use_cases.run_research_worker import (
    RunResearchWorkerUseCase,
)
from app.features.research_engine.domain.providers.insight_provider import InsightProvider
from app.features.research_engine.domain.providers.marketplace_data_provider import (
    MarketplaceDataProvider,
)
from app.features.research_engine.infrastructure.providers.mock_insight_provider import (
    MockInsightProvider,
)
from app.features.research_engine.infrastructure.providers.mock_marketplace_data_provider import (
    MockMarketplaceDataProvider,
)
from app.features.research_results.domain.repositories.research_result_repository import (
    ResearchResultRepository,
)
from app.features.research_results.presentation.api.dependencies import (
    get_research_result_repository,
)
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)
from app.features.research_sessions.presentation.api.dependencies import (
    get_research_session_repository,
)

_mock_marketplace_data_provider = MockMarketplaceDataProvider()
_mock_insight_provider = MockInsightProvider()


def get_marketplace_data_providers() -> dict[Marketplace, MarketplaceDataProvider]:
    return dict.fromkeys(Marketplace, _mock_marketplace_data_provider)


def get_insight_provider() -> InsightProvider:
    return _mock_insight_provider


def get_run_research_worker_use_case(
    research_session_repository: ResearchSessionRepository = Depends(  # noqa: B008
        get_research_session_repository
    ),
    research_result_repository: ResearchResultRepository = Depends(  # noqa: B008
        get_research_result_repository
    ),
    marketplace_data_providers: dict[Marketplace, MarketplaceDataProvider] = Depends(  # noqa: B008
        get_marketplace_data_providers
    ),
    insight_provider: InsightProvider = Depends(get_insight_provider),  # noqa: B008
) -> RunResearchWorkerUseCase:
    return RunResearchWorkerUseCase(
        research_session_repository,
        research_result_repository,
        marketplace_data_providers,
        insight_provider,
    )
