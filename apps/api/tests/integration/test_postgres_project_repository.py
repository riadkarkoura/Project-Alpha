from uuid import uuid4

from app.features.projects.infrastructure.database.repositories.postgres_project_repository import (
    PostgresProjectRepository,
)


async def test_create_persists_and_returns_project(db_pool):
    repository = PostgresProjectRepository(db_pool)

    project = await repository.create("Kitchen Research")

    assert project.name == "Kitchen Research"
    assert project.id is not None
    assert project.created_at == project.updated_at


async def test_get_by_id_returns_created_project(db_pool):
    repository = PostgresProjectRepository(db_pool)
    created = await repository.create("Kitchen Research")

    fetched = await repository.get_by_id(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Kitchen Research"


async def test_get_by_id_returns_none_for_unknown_id(db_pool):
    repository = PostgresProjectRepository(db_pool)

    fetched = await repository.get_by_id(uuid4())

    assert fetched is None


async def test_list_all_returns_all_created_projects(db_pool):
    repository = PostgresProjectRepository(db_pool)
    first = await repository.create("First Project")
    second = await repository.create("Second Project")

    projects = await repository.list_all()
    ids = {project.id for project in projects}

    assert {first.id, second.id} <= ids
