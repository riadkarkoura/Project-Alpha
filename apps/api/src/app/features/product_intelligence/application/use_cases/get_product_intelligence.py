from app.features.product_intelligence.application.dtos import (
    GetProductIntelligenceRequestDTO,
    ProductIntelligenceDTO,
    to_dto,
)
from app.features.product_intelligence.domain.exceptions import ProductIntelligenceNotFoundError
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)


class GetProductIntelligenceUseCase:
    def __init__(self, product_repository: ProductIntelligenceRepository) -> None:
        self._product_repository = product_repository

    async def execute(self, request: GetProductIntelligenceRequestDTO) -> ProductIntelligenceDTO:
        product = await self._product_repository.get_by_id(request.product_id)
        if product is None:
            raise ProductIntelligenceNotFoundError(f"Product {request.product_id} not found.")

        return to_dto(product)
