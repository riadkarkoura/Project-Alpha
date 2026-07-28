from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.features.product_intelligence.domain.entities.product_intelligence import (
    ImageAsset,
    Pricing,
    ProductIntelligence,
    ProductIntelligenceStatus,
    PublishingMetadata,
    SeoMetadata,
    Specification,
)

_DEFAULT_SEO_METADATA = SeoMetadata()
_DEFAULT_PUBLISHING_METADATA = PublishingMetadata()


@dataclass(frozen=True)
class CreateProductIntelligenceRequestDTO:
    project_id: UUID
    research_session_id: UUID | None
    title: str
    subtitle: str | None = None
    description: str | None = None
    features: tuple[str, ...] = ()
    specifications: tuple[Specification, ...] = ()
    category: str | None = None
    tags: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    seo: SeoMetadata = _DEFAULT_SEO_METADATA
    pricing: Pricing | None = None
    images: tuple[ImageAsset, ...] = ()
    publishing: PublishingMetadata = _DEFAULT_PUBLISHING_METADATA


@dataclass(frozen=True)
class UpdateProductIntelligenceRequestDTO:
    product_id: UUID
    title: str
    subtitle: str | None = None
    description: str | None = None
    features: tuple[str, ...] = ()
    specifications: tuple[Specification, ...] = ()
    category: str | None = None
    tags: tuple[str, ...] = ()
    keywords: tuple[str, ...] = ()
    seo: SeoMetadata = _DEFAULT_SEO_METADATA
    pricing: Pricing | None = None
    images: tuple[ImageAsset, ...] = ()
    publishing: PublishingMetadata = _DEFAULT_PUBLISHING_METADATA


@dataclass(frozen=True)
class GetProductIntelligenceRequestDTO:
    product_id: UUID


@dataclass(frozen=True)
class DeleteProductIntelligenceRequestDTO:
    product_id: UUID


@dataclass(frozen=True)
class MarkReadyForPublishingRequestDTO:
    product_id: UUID


@dataclass(frozen=True)
class ListProductIntelligenceRequestDTO:
    project_id: UUID


@dataclass(frozen=True)
class ProductIntelligenceDTO:
    id: UUID
    project_id: UUID
    research_session_id: UUID | None
    title: str
    subtitle: str | None
    description: str | None
    features: tuple[str, ...]
    specifications: tuple[Specification, ...]
    category: str | None
    tags: tuple[str, ...]
    keywords: tuple[str, ...]
    seo: SeoMetadata
    pricing: Pricing | None
    images: tuple[ImageAsset, ...]
    publishing: PublishingMetadata
    status: ProductIntelligenceStatus
    created_at: datetime
    updated_at: datetime


def to_dto(product: ProductIntelligence) -> ProductIntelligenceDTO:
    return ProductIntelligenceDTO(
        id=product.id,
        project_id=product.project_id,
        research_session_id=product.research_session_id,
        title=product.title,
        subtitle=product.subtitle,
        description=product.description,
        features=product.features,
        specifications=product.specifications,
        category=product.category,
        tags=product.tags,
        keywords=product.keywords,
        seo=product.seo,
        pricing=product.pricing,
        images=product.images,
        publishing=product.publishing,
        status=product.status,
        created_at=product.created_at,
        updated_at=product.updated_at,
    )
