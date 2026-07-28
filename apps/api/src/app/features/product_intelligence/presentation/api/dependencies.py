import asyncpg
from fastapi import Depends

from app.features.product_intelligence.application.use_cases.create_product_intelligence import (
    CreateProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.delete_product_intelligence import (
    DeleteProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.get_product_intelligence import (
    GetProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.list_product_intelligence import (
    ListProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.mark_ready_for_publishing import (
    MarkReadyForPublishingUseCase,
)
from app.features.product_intelligence.application.use_cases.update_product_intelligence import (
    UpdateProductIntelligenceUseCase,
)
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)
from app.features.product_intelligence.infrastructure.database.repositories.postgres_product_intelligence_repository import (  # noqa: E501
    PostgresProductIntelligenceRepository,
)
from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.projects.presentation.api.dependencies import get_project_repository
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)
from app.features.research_sessions.presentation.api.dependencies import (
    get_research_session_repository,
)
from app.infrastructure.database.connection import get_pool


async def get_product_intelligence_repository(
    pool: asyncpg.Pool = Depends(get_pool),  # noqa: B008
) -> ProductIntelligenceRepository:
    return PostgresProductIntelligenceRepository(pool)


def get_create_product_intelligence_use_case(
    product_repository: ProductIntelligenceRepository = Depends(  # noqa: B008
        get_product_intelligence_repository
    ),
    project_repository: ProjectRepository = Depends(get_project_repository),  # noqa: B008
    research_session_repository: ResearchSessionRepository = Depends(  # noqa: B008
        get_research_session_repository
    ),
) -> CreateProductIntelligenceUseCase:
    return CreateProductIntelligenceUseCase(
        product_repository, project_repository, research_session_repository
    )


def get_get_product_intelligence_use_case(
    product_repository: ProductIntelligenceRepository = Depends(  # noqa: B008
        get_product_intelligence_repository
    ),
) -> GetProductIntelligenceUseCase:
    return GetProductIntelligenceUseCase(product_repository)


def get_list_product_intelligence_use_case(
    product_repository: ProductIntelligenceRepository = Depends(  # noqa: B008
        get_product_intelligence_repository
    ),
    project_repository: ProjectRepository = Depends(get_project_repository),  # noqa: B008
) -> ListProductIntelligenceUseCase:
    return ListProductIntelligenceUseCase(product_repository, project_repository)


def get_update_product_intelligence_use_case(
    product_repository: ProductIntelligenceRepository = Depends(  # noqa: B008
        get_product_intelligence_repository
    ),
) -> UpdateProductIntelligenceUseCase:
    return UpdateProductIntelligenceUseCase(product_repository)


def get_delete_product_intelligence_use_case(
    product_repository: ProductIntelligenceRepository = Depends(  # noqa: B008
        get_product_intelligence_repository
    ),
) -> DeleteProductIntelligenceUseCase:
    return DeleteProductIntelligenceUseCase(product_repository)


def get_mark_ready_for_publishing_use_case(
    product_repository: ProductIntelligenceRepository = Depends(  # noqa: B008
        get_product_intelligence_repository
    ),
) -> MarkReadyForPublishingUseCase:
    return MarkReadyForPublishingUseCase(product_repository)
