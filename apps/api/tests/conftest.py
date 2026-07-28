import dataclasses
from collections.abc import Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.core.security import verify_api_key
from app.features.product_intelligence.domain.entities.product_intelligence import (
    ImageAsset,
    Pricing,
    ProductIntelligence,
    ProductIntelligenceStatus,
    PublishingMetadata,
    SeoMetadata,
    Specification,
)
from app.features.product_intelligence.domain.repositories.product_intelligence_repository import (
    DEFAULT_PUBLISHING_METADATA,
    DEFAULT_SEO_METADATA,
    ProductIntelligenceRepository,
)
from app.features.projects.domain.entities.project import Project
from app.features.projects.domain.repositories.project_repository import ProjectRepository
from app.features.research_results.domain.entities.research_result import ResearchResult
from app.features.research_results.domain.repositories.research_result_repository import (
    ResearchResultRepository,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSession,
    ResearchSessionStatus,
)
from app.features.research_sessions.domain.repositories.research_session_repository import (
    ResearchSessionRepository,
)


class FakeProjectRepository(ProjectRepository):
    def __init__(self) -> None:
        self.created_names: list[str] = []
        self._projects: dict[UUID, Project] = {}

    async def create(self, name: str) -> Project:
        now = datetime.now(UTC)
        project = Project(id=uuid4(), name=name, created_at=now, updated_at=now)
        self.created_names.append(name)
        self._projects[project.id] = project
        return project

    async def get_by_id(self, project_id: UUID) -> Project | None:
        return self._projects.get(project_id)

    async def list_all(self) -> list[Project]:
        return sorted(self._projects.values(), key=lambda project: project.created_at, reverse=True)


class FakeResearchSessionRepository(ResearchSessionRepository):
    def __init__(self) -> None:
        self.created: list[tuple[UUID, Marketplace]] = []
        self._sessions: dict[UUID, ResearchSession] = {}

    async def create(self, project_id: UUID, marketplace: Marketplace) -> ResearchSession:
        now = datetime.now(UTC)
        session = ResearchSession(
            id=uuid4(),
            project_id=project_id,
            marketplace=marketplace,
            status=ResearchSessionStatus.PENDING,
            created_at=now,
            updated_at=now,
        )
        self.created.append((project_id, marketplace))
        self._sessions[session.id] = session
        return session

    async def get_by_id(self, research_session_id: UUID) -> ResearchSession | None:
        return self._sessions.get(research_session_id)

    async def list_by_project_id(self, project_id: UUID) -> list[ResearchSession]:
        sessions = [s for s in self._sessions.values() if s.project_id == project_id]
        return sorted(sessions, key=lambda session: session.created_at, reverse=True)

    async def update_status(
        self, research_session_id: UUID, status: ResearchSessionStatus
    ) -> ResearchSession:
        session = self._sessions[research_session_id]
        updated = ResearchSession(
            id=session.id,
            project_id=session.project_id,
            marketplace=session.marketplace,
            status=status,
            created_at=session.created_at,
            updated_at=datetime.now(UTC),
        )
        self._sessions[research_session_id] = updated
        return updated


class FakeResearchResultRepository(ResearchResultRepository):
    def __init__(self) -> None:
        self.created: list[UUID] = []
        self._results: dict[UUID, ResearchResult] = {}

    async def create(
        self,
        research_session_id: UUID,
        opportunity_score: int,
        demand_level: str,
        competition_level: str,
        profit_level: str,
        summary: str,
    ) -> ResearchResult:
        now = datetime.now(UTC)
        result = ResearchResult(
            id=uuid4(),
            research_session_id=research_session_id,
            opportunity_score=opportunity_score,
            demand_level=demand_level,
            competition_level=competition_level,
            profit_level=profit_level,
            summary=summary,
            created_at=now,
            updated_at=now,
        )
        self.created.append(research_session_id)
        self._results[research_session_id] = result
        return result

    async def get_by_research_session_id(self, research_session_id: UUID) -> ResearchResult | None:
        return self._results.get(research_session_id)


class FakeProductIntelligenceRepository(ProductIntelligenceRepository):
    def __init__(self) -> None:
        self._products: dict[UUID, ProductIntelligence] = {}

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
        now = datetime.now(UTC)
        product = ProductIntelligence(
            id=uuid4(),
            project_id=project_id,
            research_session_id=research_session_id,
            title=title,
            subtitle=subtitle,
            description=description,
            features=tuple(features),
            specifications=tuple(specifications),
            category=category,
            tags=tuple(tags),
            keywords=tuple(keywords),
            seo=seo,
            pricing=pricing,
            images=tuple(images),
            publishing=publishing,
            status=ProductIntelligenceStatus.DRAFT,
            created_at=now,
            updated_at=now,
        )
        self._products[product.id] = product
        return product

    async def get_by_id(self, product_id: UUID) -> ProductIntelligence | None:
        return self._products.get(product_id)

    async def list_by_project_id(self, project_id: UUID) -> list[ProductIntelligence]:
        products = [p for p in self._products.values() if p.project_id == project_id]
        return sorted(products, key=lambda product: product.created_at, reverse=True)

    async def update(self, product: ProductIntelligence) -> ProductIntelligence:
        if product.id not in self._products:
            raise ValueError(f"Product {product.id} not found.")
        updated = dataclasses.replace(product, updated_at=datetime.now(UTC))
        self._products[product.id] = updated
        return updated

    async def delete(self, product_id: UUID) -> None:
        self._products.pop(product_id, None)


@pytest.fixture
def fake_project_repository() -> FakeProjectRepository:
    return FakeProjectRepository()


@pytest.fixture
def fake_research_session_repository() -> FakeResearchSessionRepository:
    return FakeResearchSessionRepository()


@pytest.fixture
def fake_research_result_repository() -> FakeResearchResultRepository:
    return FakeResearchResultRepository()


@pytest.fixture
def fake_product_intelligence_repository() -> FakeProductIntelligenceRepository:
    return FakeProductIntelligenceRepository()


@pytest.fixture(autouse=True)
def bypass_api_key_auth():
    from app.main import app

    app.dependency_overrides[verify_api_key] = lambda: None
    yield
    app.dependency_overrides.pop(verify_api_key, None)
