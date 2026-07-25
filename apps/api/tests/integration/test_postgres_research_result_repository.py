from app.features.projects.infrastructure.database.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)
from app.features.research_results.infrastructure.database.repositories.postgres_research_result_repository import (  # noqa: E501
    PostgresResearchResultRepository,
)
from app.features.research_sessions.domain.entities.research_session import Marketplace
from app.features.research_sessions.infrastructure.database.repositories.postgres_research_session_repository import (  # noqa: E501
    PostgresResearchSessionRepository,
)


async def _create_session(db_pool):
    project = await PostgresProjectRepository(db_pool).create("Kitchen Research")
    return await PostgresResearchSessionRepository(db_pool).create(project.id, Marketplace.AMAZON)


async def test_create_persists_and_returns_result(db_pool):
    session = await _create_session(db_pool)
    repository = PostgresResearchResultRepository(db_pool)

    result = await repository.create(
        research_session_id=session.id,
        opportunity_score=84,
        demand_level="high",
        competition_level="medium",
        profit_level="good",
        summary="Looks promising.",
    )

    assert result.research_session_id == session.id
    assert result.opportunity_score == 84


async def test_get_by_research_session_id_returns_none_when_absent(db_pool):
    session = await _create_session(db_pool)
    repository = PostgresResearchResultRepository(db_pool)

    fetched = await repository.get_by_research_session_id(session.id)

    assert fetched is None


async def test_get_by_research_session_id_returns_created_result(db_pool):
    session = await _create_session(db_pool)
    repository = PostgresResearchResultRepository(db_pool)
    created = await repository.create(
        research_session_id=session.id,
        opportunity_score=84,
        demand_level="high",
        competition_level="medium",
        profit_level="good",
        summary="Looks promising.",
    )

    fetched = await repository.get_by_research_session_id(session.id)

    assert fetched is not None
    assert fetched.id == created.id
