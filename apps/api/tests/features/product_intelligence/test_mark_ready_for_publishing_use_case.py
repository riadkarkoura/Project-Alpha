from decimal import Decimal
from uuid import uuid4

import pytest

from app.features.product_intelligence.application.dtos import MarkReadyForPublishingRequestDTO
from app.features.product_intelligence.application.use_cases.mark_ready_for_publishing import (
    MarkReadyForPublishingUseCase,
)
from app.features.product_intelligence.domain.entities.product_intelligence import Pricing
from app.features.product_intelligence.domain.exceptions import (
    ProductIntelligenceNotFoundError,
    ProductNotReadyForPublishingError,
)


async def test_execute_marks_a_complete_product_ready(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id,
        research_session_id=None,
        title="Bamboo Cutting Board",
        description="A durable, sustainable kitchen essential.",
        pricing=Pricing(amount=Decimal("19.99"), currency="USD"),
    )
    use_case = MarkReadyForPublishingUseCase(fake_product_intelligence_repository)

    result = await use_case.execute(MarkReadyForPublishingRequestDTO(product_id=product.id))

    assert result.status.value == "ready_for_publishing"
    persisted = await fake_product_intelligence_repository.get_by_id(product.id)
    assert persisted.status.value == "ready_for_publishing"


async def test_execute_raises_when_product_is_incomplete(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )
    use_case = MarkReadyForPublishingUseCase(fake_product_intelligence_repository)

    with pytest.raises(ProductNotReadyForPublishingError):
        await use_case.execute(MarkReadyForPublishingRequestDTO(product_id=product.id))

    persisted = await fake_product_intelligence_repository.get_by_id(product.id)
    assert persisted.status.value == "draft"


async def test_execute_raises_when_product_does_not_exist(fake_product_intelligence_repository):
    use_case = MarkReadyForPublishingUseCase(fake_product_intelligence_repository)

    with pytest.raises(ProductIntelligenceNotFoundError):
        await use_case.execute(MarkReadyForPublishingRequestDTO(product_id=uuid4()))
