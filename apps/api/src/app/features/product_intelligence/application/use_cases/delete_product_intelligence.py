from app.features.product_intelligence.application.dtos import DeleteProductIntelligenceRequestDTO
from app.features.product_intelligence.domain.exceptions import ProductIntelligenceNotFoundError
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)


class DeleteProductIntelligenceUseCase:
    def __init__(self, product_repository: ProductIntelligenceRepository) -> None:
        self._product_repository = product_repository

    async def execute(self, request: DeleteProductIntelligenceRequestDTO) -> None:
        existing = await self._product_repository.get_by_id(request.product_id)
        if existing is None:
            raise ProductIntelligenceNotFoundError(f"Product {request.product_id} not found.")

        await self._product_repository.delete(request.product_id)
