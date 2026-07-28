from uuid import uuid4

import pytest

from app.features.product_intelligence.application.dtos import (
    GetProductIntelligenceRequestDTO,
    ListProductIntelligenceRequestDTO,
)
from app.features.product_intelligence.application.use_cases.get_product_intelligence import (
    GetProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.list_product_intelligence import (
    ListProductIntelligenceUseCase,
)
from app.features.product_intelligence.domain.exceptions import ProductIntelligenceNotFoundError
from app.features.projects.domain.exceptions import ProjectNotFoundError


async def test_get_returns_existing_product(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )
    use_case = GetProductIntelligenceUseCase(fake_product_intelligence_repository)

    result = await use_case.execute(GetProductIntelligenceRequestDTO(product_id=product.id))

    assert result.id == product.id
    assert result.title == "Bamboo Cutting Board"


async def test_get_raises_when_product_does_not_exist(fake_product_intelligence_repository):
    use_case = GetProductIntelligenceUseCase(fake_product_intelligence_repository)

    with pytest.raises(ProductIntelligenceNotFoundError):
        await use_case.execute(GetProductIntelligenceRequestDTO(product_id=uuid4()))


async def test_list_returns_only_products_for_the_given_project(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    other_project = await fake_project_repository.create("Garage Research")
    await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )
    await fake_product_intelligence_repository.create(
        project_id=other_project.id, research_session_id=None, title="Socket Wrench Set"
    )
    use_case = ListProductIntelligenceUseCase(
        fake_product_intelligence_repository, fake_project_repository
    )

    result = await use_case.execute(ListProductIntelligenceRequestDTO(project_id=project.id))

    assert [product.title for product in result] == ["Bamboo Cutting Board"]


async def test_list_raises_when_project_does_not_exist(
    fake_product_intelligence_repository, fake_project_repository
):
    use_case = ListProductIntelligenceUseCase(
        fake_product_intelligence_repository, fake_project_repository
    )

    with pytest.raises(ProjectNotFoundError):
        await use_case.execute(ListProductIntelligenceRequestDTO(project_id=uuid4()))
