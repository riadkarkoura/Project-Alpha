from app.features.product_intelligence.application.dtos import (
    ListProductIntelligenceRequestDTO,
    ProductIntelligenceDTO,
    to_dto,
)
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)
from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.projects.domain.repositories.project_repository import ProjectRepository


class ListProductIntelligenceUseCase:
    def __init__(
        self,
        product_repository: ProductIntelligenceRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._product_repository = product_repository
        self._project_repository = project_repository

    async def execute(
        self, request: ListProductIntelligenceRequestDTO
    ) -> list[ProductIntelligenceDTO]:
        project = await self._project_repository.get_by_id(request.project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {request.project_id} not found.")

        products = await self._product_repository.list_by_project_id(request.project_id)
        return [to_dto(product) for product in products]
