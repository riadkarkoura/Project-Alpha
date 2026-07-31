from app.features.product_intelligence.application.dtos import (
    GeneratedProductDescriptionDTO,
    GenerateProductDescriptionRequestDTO,
)
from app.features.product_intelligence.domain.exceptions import (
    AIGenerationFailedError,
    ProductIntelligenceNotFoundError,
)
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)
from app.features.product_intelligence.infrastructure.ai.generate_description_capability import (
    GENERATE_PRODUCT_DESCRIPTION,
)
from app.shared.ai.application.execution_engine import AIExecutionEngine
from app.shared.ai.domain.entities.ai_job import AIJob


class GenerateProductDescriptionUseCase:
    """Generates a draft description and returns it - it never writes to
    the product. Accepting a draft is just a normal
    UpdateProductIntelligence call with the draft text as the new
    description; there is no separate "accept" endpoint or persisted
    draft state, on purpose - the smallest design that gives the user a
    real preview/discard choice.
    """

    def __init__(
        self,
        product_repository: ProductIntelligenceRepository,
        ai_execution_engine: AIExecutionEngine,
    ) -> None:
        self._product_repository = product_repository
        self._ai_execution_engine = ai_execution_engine

    async def execute(
        self, request: GenerateProductDescriptionRequestDTO
    ) -> GeneratedProductDescriptionDTO:
        product = await self._product_repository.get_by_id(request.product_id)
        if product is None:
            raise ProductIntelligenceNotFoundError(f"Product {request.product_id} not found.")

        job = AIJob.create(
            capability=GENERATE_PRODUCT_DESCRIPTION,
            input_data={
                "title": product.title,
                "subtitle": product.subtitle or "",
                "category": product.category or "",
            },
        )
        result = await self._ai_execution_engine.execute(job)

        if not result.is_success or result.output is None:
            raise AIGenerationFailedError(
                result.error or "AI provider returned no output."
            )

        return GeneratedProductDescriptionDTO(
            product_id=product.id, description=result.output["description"]
        )
