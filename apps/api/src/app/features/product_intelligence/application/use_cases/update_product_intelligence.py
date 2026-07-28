import dataclasses

from app.features.product_intelligence.application.dtos import (
    ProductIntelligenceDTO,
    UpdateProductIntelligenceRequestDTO,
    to_dto,
)
from app.features.product_intelligence.domain.exceptions import (
    InvalidProductIntelligenceError,
    ProductIntelligenceNotFoundError,
)
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200


class UpdateProductIntelligenceUseCase:
    """Full-replace (PUT-style) update: the caller supplies the complete new
    content. Identity, project/research linkage, status, and timestamps are
    not editable through this use case - status only changes via
    MarkReadyForPublishingUseCase (or the future Publishing Engine)."""

    def __init__(self, product_repository: ProductIntelligenceRepository) -> None:
        self._product_repository = product_repository

    async def execute(
        self, request: UpdateProductIntelligenceRequestDTO
    ) -> ProductIntelligenceDTO:
        title = self._validate_title(request.title)

        existing = await self._product_repository.get_by_id(request.product_id)
        if existing is None:
            raise ProductIntelligenceNotFoundError(f"Product {request.product_id} not found.")

        updated = dataclasses.replace(
            existing,
            title=title,
            subtitle=request.subtitle,
            description=request.description,
            features=request.features,
            specifications=request.specifications,
            category=request.category,
            tags=request.tags,
            keywords=request.keywords,
            seo=request.seo,
            pricing=request.pricing,
            images=request.images,
            publishing=request.publishing,
        )
        saved = await self._product_repository.update(updated)
        return to_dto(saved)

    @staticmethod
    def _validate_title(title: str) -> str:
        trimmed = title.strip()
        if len(trimmed) < MIN_TITLE_LENGTH:
            raise InvalidProductIntelligenceError(
                f"Product title must be at least {MIN_TITLE_LENGTH} characters."
            )
        if len(trimmed) > MAX_TITLE_LENGTH:
            raise InvalidProductIntelligenceError(
                f"Product title must be at most {MAX_TITLE_LENGTH} characters."
            )
        return trimmed
