from app.features.product_intelligence.application.dtos import (
    MarkReadyForPublishingRequestDTO,
    ProductIntelligenceDTO,
    to_dto,
)
from app.features.product_intelligence.domain.exceptions import ProductIntelligenceNotFoundError
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)


class MarkReadyForPublishingUseCase:
    """Application-layer wiring only: the actual publish-readiness rule lives
    on the ProductIntelligence aggregate (`mark_ready_for_publishing`)."""

    def __init__(self, product_repository: ProductIntelligenceRepository) -> None:
        self._product_repository = product_repository

    async def execute(
        self, request: MarkReadyForPublishingRequestDTO
    ) -> ProductIntelligenceDTO:
        product = await self._product_repository.get_by_id(request.product_id)
        if product is None:
            raise ProductIntelligenceNotFoundError(f"Product {request.product_id} not found.")

        ready = product.mark_ready_for_publishing()
        saved = await self._product_repository.update(ready)
        return to_dto(saved)
