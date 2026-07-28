import dataclasses
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID

from app.features.product_intelligence.domain.exceptions import (
    ProductNotReadyForPublishingError,
)


class ProductIntelligenceStatus(StrEnum):
    DRAFT = "draft"
    READY_FOR_PUBLISHING = "ready_for_publishing"
    PUBLISHED = "published"


@dataclass(frozen=True)
class SeoMetadata:
    """Search-engine metadata. Every field is optional - a draft product may
    not have SEO content decided yet."""

    meta_title: str | None = None
    meta_description: str | None = None
    slug: str | None = None


@dataclass(frozen=True)
class Pricing:
    """Money is deliberately narrow for Phase 1 (a single list price). Sale
    prices, cost prices, and multi-currency support are additive extensions,
    not a redesign, when pricing logic is built."""

    amount: Decimal
    currency: str
    compare_at_amount: Decimal | None = None

    def __post_init__(self) -> None:
        if self.amount < 0:
            raise ValueError("Pricing amount cannot be negative.")
        if len(self.currency) != 3:
            raise ValueError("Pricing currency must be a 3-letter code (e.g. USD).")
        if self.compare_at_amount is not None and self.compare_at_amount < 0:
            raise ValueError("Pricing compare_at_amount cannot be negative.")


@dataclass(frozen=True)
class ImageAsset:
    url: str
    alt_text: str | None = None


@dataclass(frozen=True)
class Specification:
    name: str
    value: str


@dataclass(frozen=True)
class PublishingMetadata:
    """Placeholder shape for the future Publishing Engine. Per-channel
    external ids (e.g. a Shopify product gid) are added later as new fields;
    the aggregate itself does not need to change shape to support them."""

    published_channels: tuple[str, ...] = ()
    published_at: datetime | None = None


_ReadinessCheck = Callable[["ProductIntelligence"], bool]

_READY_FOR_PUBLISHING_REQUIREMENTS: tuple[tuple[str, _ReadinessCheck], ...] = (
    ("title", lambda product: bool(product.title.strip())),
    ("description", lambda product: bool((product.description or "").strip())),
    ("pricing", lambda product: product.pricing is not None),
)


@dataclass(frozen=True)
class ProductIntelligence:
    """The canonical, publishable product record.

    This aggregate is intentionally the single source of truth for a
    product's content, independent of any marketplace, AI provider, or
    storefront connector. New capabilities (AI-generated content, publishing
    to Shopify/WooCommerce/HomeNest, etc.) are expected to read and write
    this aggregate rather than each inventing their own product shape.
    """

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

    def mark_ready_for_publishing(self) -> "ProductIntelligence":
        """Business rule: a product can only move to READY_FOR_PUBLISHING once
        it has the minimum content a storefront needs. This lives on the
        aggregate (not the use case) because it is a product-content
        invariant, not an application workflow concern.
        """
        missing = [
            requirement
            for requirement, is_satisfied in _READY_FOR_PUBLISHING_REQUIREMENTS
            if not is_satisfied(self)
        ]
        if missing:
            raise ProductNotReadyForPublishingError(
                f"Product {self.id} is missing required fields before it can be marked "
                f"ready for publishing: {', '.join(missing)}."
            )

        return dataclasses.replace(self, status=ProductIntelligenceStatus.READY_FOR_PUBLISHING)


__all__ = [
    "ImageAsset",
    "Pricing",
    "ProductIntelligence",
    "ProductIntelligenceStatus",
    "PublishingMetadata",
    "SeoMetadata",
    "Specification",
]
