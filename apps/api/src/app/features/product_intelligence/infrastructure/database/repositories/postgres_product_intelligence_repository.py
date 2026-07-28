from collections.abc import Sequence
from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import asyncpg

from app.features.product_intelligence.domain.entities.product_intelligence import (
    ImageAsset,
    Pricing,
    ProductIntelligence,
    ProductIntelligenceStatus,
    PublishingMetadata,
    SeoMetadata,
    Specification,
)
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    DEFAULT_PUBLISHING_METADATA,
    DEFAULT_SEO_METADATA,
    ProductIntelligenceRepository,
)

_INSERT_QUERY = """
    INSERT INTO product_intelligence (
        project_id, research_session_id, title, subtitle, description, features,
        specifications, category, tags, keywords, seo_metadata, pricing,
        image_metadata, publishing_metadata
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
    RETURNING
        id, project_id, research_session_id, title, subtitle, description, features,
        specifications, category, tags, keywords, seo_metadata, pricing,
        image_metadata, publishing_metadata, status, created_at, updated_at
"""

_SELECT_BY_ID_QUERY = """
    SELECT
        id, project_id, research_session_id, title, subtitle, description, features,
        specifications, category, tags, keywords, seo_metadata, pricing,
        image_metadata, publishing_metadata, status, created_at, updated_at
    FROM product_intelligence
    WHERE id = $1
"""

_SELECT_BY_PROJECT_ID_QUERY = """
    SELECT
        id, project_id, research_session_id, title, subtitle, description, features,
        specifications, category, tags, keywords, seo_metadata, pricing,
        image_metadata, publishing_metadata, status, created_at, updated_at
    FROM product_intelligence
    WHERE project_id = $1
    ORDER BY created_at DESC
"""

_UPDATE_QUERY = """
    UPDATE product_intelligence
    SET
        title = $2, subtitle = $3, description = $4, features = $5,
        specifications = $6, category = $7, tags = $8, keywords = $9,
        seo_metadata = $10, pricing = $11, image_metadata = $12,
        publishing_metadata = $13, status = $14
    WHERE id = $1
    RETURNING
        id, project_id, research_session_id, title, subtitle, description, features,
        specifications, category, tags, keywords, seo_metadata, pricing,
        image_metadata, publishing_metadata, status, created_at, updated_at
"""

_DELETE_QUERY = "DELETE FROM product_intelligence WHERE id = $1"


def _specification_to_json(spec: Specification) -> dict[str, str]:
    return {"name": spec.name, "value": spec.value}


def _specification_from_json(data: dict[str, Any]) -> Specification:
    return Specification(name=data["name"], value=data["value"])


def _image_to_json(image: ImageAsset) -> dict[str, str | None]:
    return {"url": image.url, "alt_text": image.alt_text}


def _image_from_json(data: dict[str, Any]) -> ImageAsset:
    return ImageAsset(url=data["url"], alt_text=data.get("alt_text"))


def _seo_to_json(seo: SeoMetadata) -> dict[str, str | None]:
    return {
        "meta_title": seo.meta_title,
        "meta_description": seo.meta_description,
        "slug": seo.slug,
    }


def _seo_from_json(data: dict[str, Any]) -> SeoMetadata:
    return SeoMetadata(
        meta_title=data.get("meta_title"),
        meta_description=data.get("meta_description"),
        slug=data.get("slug"),
    )


def _pricing_to_json(pricing: Pricing | None) -> dict[str, str | None] | None:
    if pricing is None:
        return None
    return {
        "amount": str(pricing.amount),
        "currency": pricing.currency,
        "compare_at_amount": str(pricing.compare_at_amount)
        if pricing.compare_at_amount is not None
        else None,
    }


def _pricing_from_json(data: dict[str, Any] | None) -> Pricing | None:
    if data is None:
        return None
    compare_at = data.get("compare_at_amount")
    return Pricing(
        amount=Decimal(data["amount"]),
        currency=data["currency"],
        compare_at_amount=Decimal(compare_at) if compare_at is not None else None,
    )


def _publishing_to_json(publishing: PublishingMetadata) -> dict[str, Any]:
    return {
        "published_channels": list(publishing.published_channels),
        "published_at": publishing.published_at.isoformat() if publishing.published_at else None,
    }


def _publishing_from_json(data: dict[str, Any]) -> PublishingMetadata:
    published_at = data.get("published_at")
    return PublishingMetadata(
        published_channels=tuple(data.get("published_channels", [])),
        published_at=datetime.fromisoformat(published_at) if published_at else None,
    )


class PostgresProductIntelligenceRepository(ProductIntelligenceRepository):
    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def create(
        self,
        *,
        project_id: UUID,
        research_session_id: UUID | None,
        title: str,
        subtitle: str | None = None,
        description: str | None = None,
        features: Sequence[str] = (),
        specifications: Sequence[Specification] = (),
        category: str | None = None,
        tags: Sequence[str] = (),
        keywords: Sequence[str] = (),
        seo: SeoMetadata = DEFAULT_SEO_METADATA,
        pricing: Pricing | None = None,
        images: Sequence[ImageAsset] = (),
        publishing: PublishingMetadata = DEFAULT_PUBLISHING_METADATA,
    ) -> ProductIntelligence:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                _INSERT_QUERY,
                project_id,
                research_session_id,
                title,
                subtitle,
                description,
                list(features),
                [_specification_to_json(spec) for spec in specifications],
                category,
                list(tags),
                list(keywords),
                _seo_to_json(seo),
                _pricing_to_json(pricing),
                [_image_to_json(image) for image in images],
                _publishing_to_json(publishing),
            )

        return self._to_entity(row)

    async def get_by_id(self, product_id: UUID) -> ProductIntelligence | None:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(_SELECT_BY_ID_QUERY, product_id)

        if row is None:
            return None

        return self._to_entity(row)

    async def list_by_project_id(self, project_id: UUID) -> list[ProductIntelligence]:
        async with self._pool.acquire() as connection:
            rows = await connection.fetch(_SELECT_BY_PROJECT_ID_QUERY, project_id)

        return [self._to_entity(row) for row in rows]

    async def update(self, product: ProductIntelligence) -> ProductIntelligence:
        async with self._pool.acquire() as connection:
            row = await connection.fetchrow(
                _UPDATE_QUERY,
                product.id,
                product.title,
                product.subtitle,
                product.description,
                list(product.features),
                [_specification_to_json(spec) for spec in product.specifications],
                product.category,
                list(product.tags),
                list(product.keywords),
                _seo_to_json(product.seo),
                _pricing_to_json(product.pricing),
                [_image_to_json(image) for image in product.images],
                _publishing_to_json(product.publishing),
                product.status.value,
            )

        if row is None:
            raise ValueError(f"Product {product.id} not found.")

        return self._to_entity(row)

    async def delete(self, product_id: UUID) -> None:
        async with self._pool.acquire() as connection:
            await connection.execute(_DELETE_QUERY, product_id)

    @staticmethod
    def _to_entity(row: asyncpg.Record) -> ProductIntelligence:
        return ProductIntelligence(
            id=row["id"],
            project_id=row["project_id"],
            research_session_id=row["research_session_id"],
            title=row["title"],
            subtitle=row["subtitle"],
            description=row["description"],
            features=tuple(row["features"]),
            specifications=tuple(
                _specification_from_json(spec) for spec in row["specifications"]
            ),
            category=row["category"],
            tags=tuple(row["tags"]),
            keywords=tuple(row["keywords"]),
            seo=_seo_from_json(row["seo_metadata"]),
            pricing=_pricing_from_json(row["pricing"]),
            images=tuple(_image_from_json(image) for image in row["image_metadata"]),
            publishing=_publishing_from_json(row["publishing_metadata"]),
            status=ProductIntelligenceStatus(row["status"]),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
