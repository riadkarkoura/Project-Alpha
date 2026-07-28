from uuid import uuid4

import pytest

from app.features.product_intelligence.application.dtos import (
    DeleteProductIntelligenceRequestDTO,
    UpdateProductIntelligenceRequestDTO,
)
from app.features.product_intelligence.application.use_cases.delete_product_intelligence import (
    DeleteProductIntelligenceUseCase,
)
from app.features.product_intelligence.application.use_cases.update_product_intelligence import (
    UpdateProductIntelligenceUseCase,
)
from app.features.product_intelligence.domain.exceptions import (
    InvalidProductIntelligenceError,
    ProductIntelligenceNotFoundError,
)


async def test_update_replaces_editable_fields(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id,
        research_session_id=None,
        title="Bamboo Cutting Board",
        subtitle=None,
    )
    use_case = UpdateProductIntelligenceUseCase(fake_product_intelligence_repository)

    result = await use_case.execute(
        UpdateProductIntelligenceRequestDTO(
            product_id=product.id,
            title="Bamboo Cutting Board XL",
            subtitle="Now bigger",
            tags=("kitchen", "eco-friendly"),
        )
    )

    assert result.title == "Bamboo Cutting Board XL"
    assert result.subtitle == "Now bigger"
    assert result.tags == ("kitchen", "eco-friendly")
    assert result.project_id == project.id


async def test_update_does_not_change_project_or_research_session_linkage(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )
    use_case = UpdateProductIntelligenceUseCase(fake_product_intelligence_repository)

    result = await use_case.execute(
        UpdateProductIntelligenceRequestDTO(product_id=product.id, title="New Title")
    )

    assert result.project_id == project.id
    assert result.research_session_id is None


@pytest.mark.parametrize("title", ["", "ab"])
async def test_update_rejects_invalid_titles(
    fake_product_intelligence_repository, fake_project_repository, title
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )
    use_case = UpdateProductIntelligenceUseCase(fake_product_intelligence_repository)

    with pytest.raises(InvalidProductIntelligenceError):
        await use_case.execute(
            UpdateProductIntelligenceRequestDTO(product_id=product.id, title=title)
        )


async def test_update_raises_when_product_does_not_exist(fake_product_intelligence_repository):
    use_case = UpdateProductIntelligenceUseCase(fake_product_intelligence_repository)

    with pytest.raises(ProductIntelligenceNotFoundError):
        await use_case.execute(
            UpdateProductIntelligenceRequestDTO(product_id=uuid4(), title="New Title")
        )


async def test_delete_removes_an_existing_product(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )
    use_case = DeleteProductIntelligenceUseCase(fake_product_intelligence_repository)

    await use_case.execute(DeleteProductIntelligenceRequestDTO(product_id=product.id))

    assert await fake_product_intelligence_repository.get_by_id(product.id) is None


async def test_delete_raises_when_product_does_not_exist(fake_product_intelligence_repository):
    use_case = DeleteProductIntelligenceUseCase(fake_product_intelligence_repository)

    with pytest.raises(ProductIntelligenceNotFoundError):
        await use_case.execute(DeleteProductIntelligenceRequestDTO(product_id=uuid4()))
