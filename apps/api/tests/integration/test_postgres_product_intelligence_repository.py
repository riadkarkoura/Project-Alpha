import dataclasses
from decimal import Decimal

from app.features.product_intelligence.domain.entities.product_intelligence import (
    ImageAsset,
    Pricing,
    ProductIntelligenceStatus,
    PublishingMetadata,
    SeoMetadata,
    Specification,
)
from app.features.product_intelligence.infrastructure.database.repositories.postgres_product_intelligence_repository import (  # noqa: E501
    PostgresProductIntelligenceRepository,
)
from app.features.projects.infrastructure.database.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)


async def test_create_persists_and_round_trips_every_value_object(db_pool):
    project = await PostgresProjectRepository(db_pool).create("Kitchen Research")
    repository = PostgresProductIntelligenceRepository(db_pool)

    created = await repository.create(
        project_id=project.id,
        research_session_id=None,
        title="Bamboo Cutting Board",
        subtitle="Sustainable and sturdy",
        description="A durable, sustainable kitchen essential.",
        features=("Non-slip base", "Reversible"),
        specifications=(Specification(name="Material", value="Bamboo"),),
        category="Kitchen",
        tags=("eco-friendly",),
        keywords=("cutting board", "bamboo"),
        seo=SeoMetadata(meta_title="Bamboo Board", slug="bamboo-board"),
        pricing=Pricing(
            amount=Decimal("19.99"), currency="USD", compare_at_amount=Decimal("24.99")
        ),
        images=(ImageAsset(url="https://example.com/board.jpg", alt_text="The board"),),
        publishing=PublishingMetadata(published_channels=("shopify",)),
    )

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.title == "Bamboo Cutting Board"
    assert fetched.features == ("Non-slip base", "Reversible")
    assert fetched.specifications == (Specification(name="Material", value="Bamboo"),)
    assert fetched.seo == SeoMetadata(meta_title="Bamboo Board", slug="bamboo-board")
    assert fetched.pricing == Pricing(
        amount=Decimal("19.99"), currency="USD", compare_at_amount=Decimal("24.99")
    )
    assert fetched.images == (
        ImageAsset(url="https://example.com/board.jpg", alt_text="The board"),
    )
    assert fetched.publishing == PublishingMetadata(published_channels=("shopify",))
    assert fetched.status == ProductIntelligenceStatus.DRAFT


async def test_create_with_no_pricing_round_trips_as_none(db_pool):
    project = await PostgresProjectRepository(db_pool).create("Kitchen Research")
    repository = PostgresProductIntelligenceRepository(db_pool)

    created = await repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.pricing is None
    assert fetched.seo == SeoMetadata()
    assert fetched.features == ()


async def test_list_by_project_id_returns_only_that_projects_products(db_pool):
    project_repository = PostgresProjectRepository(db_pool)
    repository = PostgresProductIntelligenceRepository(db_pool)
    project = await project_repository.create("Kitchen Research")
    other_project = await project_repository.create("Garage Research")
    product = await repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )
    await repository.create(
        project_id=other_project.id, research_session_id=None, title="Socket Wrench Set"
    )

    products = await repository.list_by_project_id(project.id)

    assert [p.id for p in products] == [product.id]


async def test_update_persists_new_field_values(db_pool):
    project = await PostgresProjectRepository(db_pool).create("Kitchen Research")
    repository = PostgresProductIntelligenceRepository(db_pool)
    created = await repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )

    updated_entity = dataclasses.replace(created, title="New Title", tags=("kitchen",))
    saved = await repository.update(updated_entity)

    assert saved.title == "New Title"
    assert saved.tags == ("kitchen",)
    fetched = await repository.get_by_id(created.id)
    assert fetched is not None
    assert fetched.title == "New Title"


async def test_delete_removes_the_row(db_pool):
    project = await PostgresProjectRepository(db_pool).create("Kitchen Research")
    repository = PostgresProductIntelligenceRepository(db_pool)
    created = await repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Cutting Board"
    )

    await repository.delete(created.id)

    assert await repository.get_by_id(created.id) is None
