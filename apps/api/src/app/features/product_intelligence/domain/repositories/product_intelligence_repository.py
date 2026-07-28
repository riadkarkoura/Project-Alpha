from abc import ABC, abstractmethod
from collections.abc import Sequence
from uuid import UUID

from app.features.product_intelligence.domain.entities.product_intelligence import (
    ImageAsset,
    Pricing,
    ProductIntelligence,
    PublishingMetadata,
    SeoMetadata,
    Specification,
)

DEFAULT_SEO_METADATA = SeoMetadata()
DEFAULT_PUBLISHING_METADATA = PublishingMetadata()


class ProductIntelligenceRepository(ABC):
    @abstractmethod
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
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, product_id: UUID) -> ProductIntelligence | None:
        raise NotImplementedError

    @abstractmethod
    async def list_by_project_id(self, project_id: UUID) -> list[ProductIntelligence]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, product: ProductIntelligence) -> ProductIntelligence:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, product_id: UUID) -> None:
        raise NotImplementedError
