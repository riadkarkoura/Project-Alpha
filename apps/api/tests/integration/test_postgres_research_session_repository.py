from uuid import uuid4

from app.features.projects.infrastructure.database.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSessionStatus,
)
from app.features.research_sessions.infrastructure.database.repositories.postgres_research_session_repository import (  # noqa: E501
    PostgresResearchSessionRepository,
)


async def test_create_persists_and_returns_pending_session(db_pool):
    project = await PostgresProjectRepository(db_pool).create("Kitchen Research")
    repository = PostgresResearchSessionRepository(db_pool)

    session = await repository.create(project.id, Marketplace.AMAZON)

    assert session.project_id == project.id
    assert session.marketplace == Marketplace.AMAZON
    assert session.status == ResearchSessionStatus.PENDING


async def test_get_by_id_returns_none_for_unknown_id(db_pool):
    repository = PostgresResearchSessionRepository(db_pool)

    fetched = await repository.get_by_id(uuid4())

    assert fetched is None


async def test_list_by_project_id_returns_only_sessions_for_that_project(db_pool):
    project_repository = PostgresProjectRepository(db_pool)
    session_repository = PostgresResearchSessionRepository(db_pool)
    project = await project_repository.create("Kitchen Research")
    other_project = await project_repository.create("Garage Research")
    session = await session_repository.create(project.id, Marketplace.AMAZON)
    await session_repository.create(other_project.id, Marketplace.EBAY)

    sessions = await session_repository.list_by_project_id(project.id)

    assert [s.id for s in sessions] == [session.id]


async def test_update_status_persists_new_status(db_pool):
    project = await PostgresProjectRepository(db_pool).create("Kitchen Research")
    repository = PostgresResearchSessionRepository(db_pool)
    session = await repository.create(project.id, Marketplace.AMAZON)

    updated = await repository.update_status(session.id, ResearchSessionStatus.COMPLETED)

    assert updated.status == ResearchSessionStatus.COMPLETED
    fetched = await repository.get_by_id(session.id)
    assert fetched is not None
    assert fetched.status == ResearchSessionStatus.COMPLETED
