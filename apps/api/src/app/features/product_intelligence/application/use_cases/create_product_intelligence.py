from app.features.product_intelligence.application.dtos import (
    CreateProductIntelligenceRequestDTO,
    ProductIntelligenceDTO,
    to_dto,
)
from app.features.product_intelligence.domain.exceptions import InvalidProductIntelligenceError
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    ProductIntelligenceRepository,
)
from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200


class CreateProductIntelligenceUseCase:
    def __init__(
        self,
        product_repository: ProductIntelligenceRepository,
        project_repository: ProjectRepository,
        research_session_repository: ResearchSessionRepository,
    ) -> None:
        self._product_repository = product_repository
        self._project_repository = project_repository
        self._research_session_repository = research_session_repository

    async def execute(
        self, request: CreateProductIntelligenceRequestDTO
    ) -> ProductIntelligenceDTO:
        title = self._validate_title(request.title)

        project = await self._project_repository.get_by_id(request.project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {request.project_id} not found.")

        if request.research_session_id is not None:
            session = await self._research_session_repository.get_by_id(
                request.research_session_id
            )
            if session is None:
                raise ResearchSessionNotFoundError(
                    f"Research session {request.research_session_id} not found."
                )
            if session.project_id != request.project_id:
                raise InvalidProductIntelligenceError(
                    f"Research session {request.research_session_id} does not belong to "
                    f"project {request.project_id}."
                )

        product = await self._product_repository.create(
            project_id=request.project_id,
            research_session_id=request.research_session_id,
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
        return to_dto(product)

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
