from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

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
from app.features.product_intelligence.domain.entities.product_intelligence import Pricing
from app.features.product_intelligence.presentation.api.dependencies import (
    get_create_product_intelligence_use_case,
    get_delete_product_intelligence_use_case,
    get_get_product_intelligence_use_case,
    get_list_product_intelligence_use_case,
    get_mark_ready_for_publishing_use_case,
    get_update_product_intelligence_use_case,
)
from app.main import app


@pytest.fixture
def client(
    fake_product_intelligence_repository, fake_project_repository, fake_research_session_repository
):
    app.dependency_overrides[get_create_product_intelligence_use_case] = (
        lambda: CreateProductIntelligenceUseCase(
            fake_product_intelligence_repository,
            fake_project_repository,
            fake_research_session_repository,
        )
    )
    app.dependency_overrides[get_get_product_intelligence_use_case] = (
        lambda: GetProductIntelligenceUseCase(fake_product_intelligence_repository)
    )
    app.dependency_overrides[get_list_product_intelligence_use_case] = (
        lambda: ListProductIntelligenceUseCase(
            fake_product_intelligence_repository, fake_project_repository
        )
    )
    app.dependency_overrides[get_update_product_intelligence_use_case] = (
        lambda: UpdateProductIntelligenceUseCase(fake_product_intelligence_repository)
    )
    app.dependency_overrides[get_delete_product_intelligence_use_case] = (
        lambda: DeleteProductIntelligenceUseCase(fake_product_intelligence_repository)
    )
    app.dependency_overrides[get_mark_ready_for_publishing_use_case] = (
        lambda: MarkReadyForPublishingUseCase(fake_product_intelligence_repository)
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


async def test_create_returns_201_with_draft_product(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/product-intelligence",
        json={"title": "Bamboo Cutting Board"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == str(project.id)
    assert body["title"] == "Bamboo Cutting Board"
    assert body["status"] == "draft"
    assert body["seo"] == {"meta_title": None, "meta_description": None, "slug": None}
    assert body["pricing"] is None


async def test_create_accepts_full_payload(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/product-intelligence",
        json={
            "title": "Bamboo Cutting Board",
            "subtitle": "Sustainable and sturdy",
            "description": "A durable, sustainable kitchen essential.",
            "features": ["Non-slip base", "Reversible"],
            "specifications": [{"name": "Material", "value": "Bamboo"}],
            "category": "Kitchen",
            "tags": ["eco-friendly"],
            "keywords": ["cutting board", "bamboo"],
            "seo": {"meta_title": "Bamboo Cutting Board", "slug": "bamboo-cutting-board"},
            "pricing": {"amount": "19.99", "currency": "USD"},
            "images": [{"url": "https://example.com/board.jpg", "alt_text": "The board"}],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["features"] == ["Non-slip base", "Reversible"]
    assert body["specifications"] == [{"name": "Material", "value": "Bamboo"}]
    assert body["pricing"] == {"amount": "19.99", "currency": "USD", "compare_at_amount": None}
    assert body["images"] == [{"url": "https://example.com/board.jpg", "alt_text": "The board"}]


def test_create_returns_404_for_unknown_project(client):
    response = client.post(
        f"/api/v1/projects/{uuid4()}/product-intelligence",
        json={"title": "Bamboo Cutting Board"},
    )

    assert response.status_code == 404


async def test_create_returns_422_for_invalid_title(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")

    response = client.post(
        f"/api/v1/projects/{project.id}/product-intelligence", json={"title": "a"}
    )

    assert response.status_code == 422


async def test_list_returns_products_for_the_project(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")
    client.post(
        f"/api/v1/projects/{project.id}/product-intelligence",
        json={"title": "Bamboo Cutting Board"},
    )

    response = client.get(f"/api/v1/projects/{project.id}/product-intelligence")

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_returns_404_for_unknown_project(client):
    response = client.get(f"/api/v1/projects/{uuid4()}/product-intelligence")

    assert response.status_code == 404


async def test_get_returns_existing_product(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")
    created = client.post(
        f"/api/v1/projects/{project.id}/product-intelligence",
        json={"title": "Bamboo Cutting Board"},
    ).json()

    response = client.get(f"/api/v1/product-intelligence/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "Bamboo Cutting Board"


def test_get_returns_404_for_unknown_product(client):
    response = client.get(f"/api/v1/product-intelligence/{uuid4()}")

    assert response.status_code == 404


async def test_update_replaces_content(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")
    created = client.post(
        f"/api/v1/projects/{project.id}/product-intelligence",
        json={"title": "Bamboo Cutting Board"},
    ).json()

    response = client.put(
        f"/api/v1/product-intelligence/{created['id']}",
        json={"title": "Bamboo Cutting Board XL", "tags": ["kitchen"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Bamboo Cutting Board XL"
    assert body["tags"] == ["kitchen"]


def test_update_returns_404_for_unknown_product(client):
    response = client.put(
        f"/api/v1/product-intelligence/{uuid4()}", json={"title": "New Title"}
    )

    assert response.status_code == 404


async def test_delete_removes_the_product(client, fake_project_repository):
    project = await fake_project_repository.create("Kitchen Research")
    created = client.post(
        f"/api/v1/projects/{project.id}/product-intelligence",
        json={"title": "Bamboo Cutting Board"},
    ).json()

    response = client.delete(f"/api/v1/product-intelligence/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/api/v1/product-intelligence/{created['id']}").status_code == 404


def test_delete_returns_404_for_unknown_product(client):
    response = client.delete(f"/api/v1/product-intelligence/{uuid4()}")

    assert response.status_code == 404


async def test_mark_ready_for_publishing_succeeds_when_product_is_complete(
    client, fake_project_repository, fake_product_intelligence_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id,
        research_session_id=None,
        title="Bamboo Cutting Board",
        description="A durable, sustainable kitchen essential.",
        pricing=Pricing(amount=Decimal("19.99"), currency="USD"),
    )

    response = client.post(f"/api/v1/product-intelligence/{product.id}/mark-ready-for-publishing")

    assert response.status_code == 200
    assert response.json()["status"] == "ready_for_publishing"


async def test_mark_ready_for_publishing_returns_422_when_incomplete(
    client, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    created = client.post(
        f"/api/v1/projects/{project.id}/product-intelligence",
        json={"title": "Bamboo Cutting Board"},
    ).json()

    response = client.post(
        f"/api/v1/product-intelligence/{created['id']}/mark-ready-for-publishing"
    )

    assert response.status_code == 422


def test_mark_ready_for_publishing_returns_404_for_unknown_product(client):
    response = client.post(f"/api/v1/product-intelligence/{uuid4()}/mark-ready-for-publishing")

    assert response.status_code == 404
