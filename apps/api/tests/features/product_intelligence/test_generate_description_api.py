from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.features.product_intelligence.application.use_cases.generate_product_description import (
    GenerateProductDescriptionUseCase,
)
from app.features.product_intelligence.presentation.api.dependencies import (
    get_generate_product_description_use_case,
)
from app.main import app
from app.shared.ai.domain.entities.ai_execution_result import AIExecutionResult
from app.shared.ai.domain.entities.ai_job import AIJob, AIJobResult
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName


class _FakeAIExecutionEngine:
    def __init__(self, result: AIExecutionResult) -> None:
        self._result = result

    async def execute(self, job: AIJob) -> AIExecutionResult:
        return self._result


def _successful_result(description: str) -> AIExecutionResult:
    job = AIJob.create(capability="generate_product_description", input_data={}).start()
    result = AIJobResult(output={"description": description}, provider=AIProviderName.MOCK)
    return AIExecutionResult(job=job.complete(result))


def _failed_result(error: str) -> AIExecutionResult:
    job = AIJob.create(capability="generate_product_description", input_data={}).start()
    return AIExecutionResult(job=job.fail(error))


@pytest.fixture
def client(fake_product_intelligence_repository, fake_project_repository):
    def override(engine_result: AIExecutionResult):
        def _factory() -> GenerateProductDescriptionUseCase:
            return GenerateProductDescriptionUseCase(
                fake_product_intelligence_repository, _FakeAIExecutionEngine(engine_result)
            )

        return _factory

    def _set_result(engine_result: AIExecutionResult) -> TestClient:
        app.dependency_overrides[get_generate_product_description_use_case] = override(
            engine_result
        )
        return TestClient(app)

    yield _set_result
    app.dependency_overrides.clear()


async def test_generate_description_returns_the_draft_and_does_not_persist_it(
    client, fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Board"
    )
    test_client = client(_successful_result("A lovely bamboo board."))

    response = test_client.post(f"/api/v1/product-intelligence/{product.id}/generate-description")

    assert response.status_code == 200
    body = response.json()
    assert body == {"product_id": str(product.id), "description": "A lovely bamboo board."}

    persisted = await fake_product_intelligence_repository.get_by_id(product.id)
    assert persisted.description is None


def test_generate_description_returns_404_for_unknown_product(client):
    test_client = client(_successful_result("irrelevant"))

    response = test_client.post(f"/api/v1/product-intelligence/{uuid4()}/generate-description")

    assert response.status_code == 404


async def test_generate_description_returns_502_when_generation_fails(
    client, fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Board"
    )
    test_client = client(_failed_result("provider unavailable"))

    response = test_client.post(f"/api/v1/product-intelligence/{product.id}/generate-description")

    assert response.status_code == 502
