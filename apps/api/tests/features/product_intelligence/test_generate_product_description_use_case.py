from uuid import uuid4

import pytest

from app.features.product_intelligence.application.dtos import (
    GenerateProductDescriptionRequestDTO,
)
from app.features.product_intelligence.application.use_cases.generate_product_description import (
    GenerateProductDescriptionUseCase,
)
from app.features.product_intelligence.domain.exceptions import (
    AIGenerationFailedError,
    ProductIntelligenceNotFoundError,
)
from app.shared.ai.domain.entities.ai_execution_result import AIExecutionResult
from app.shared.ai.domain.entities.ai_job import AIJob, AIJobResult
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName


class _FakeAIExecutionEngine:
    """A minimal duck-typed double for AIExecutionEngine: this is a unit
    test of the use case, not of the execution engine chain (which has its
    own tests in tests/shared/ai)."""

    def __init__(self, result: AIExecutionResult) -> None:
        self._result = result
        self.executed_jobs: list[AIJob] = []

    async def execute(self, job: AIJob) -> AIExecutionResult:
        self.executed_jobs.append(job)
        return self._result


def _successful_result(description: str = "A lovely bamboo board.") -> AIExecutionResult:
    job = AIJob.create(capability="generate_product_description", input_data={}).start()
    completed = job.complete(
        AIJobResult(output={"description": description}, provider=AIProviderName.MOCK)
    )
    return AIExecutionResult(job=completed)


def _failed_result(error: str = "provider unavailable") -> AIExecutionResult:
    job = AIJob.create(capability="generate_product_description", input_data={}).start()
    failed = job.fail(error)
    return AIExecutionResult(job=failed)


async def test_execute_returns_the_generated_draft_without_saving_it(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Board", category="Kitchen"
    )
    engine = _FakeAIExecutionEngine(_successful_result("A lovely bamboo board."))
    use_case = GenerateProductDescriptionUseCase(fake_product_intelligence_repository, engine)

    result = await use_case.execute(GenerateProductDescriptionRequestDTO(product_id=product.id))

    assert result.product_id == product.id
    assert result.description == "A lovely bamboo board."

    persisted = await fake_product_intelligence_repository.get_by_id(product.id)
    assert persisted.description is None  # unchanged - no silent overwrite


async def test_execute_builds_the_job_from_the_products_own_fields(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id,
        research_session_id=None,
        title="Bamboo Board",
        subtitle="Sustainable",
        category="Kitchen",
    )
    engine = _FakeAIExecutionEngine(_successful_result())
    use_case = GenerateProductDescriptionUseCase(fake_product_intelligence_repository, engine)

    await use_case.execute(GenerateProductDescriptionRequestDTO(product_id=product.id))

    assert len(engine.executed_jobs) == 1
    job = engine.executed_jobs[0]
    assert job.input_data == {
        "title": "Bamboo Board",
        "subtitle": "Sustainable",
        "category": "Kitchen",
    }


async def test_execute_raises_when_the_product_does_not_exist(fake_product_intelligence_repository):
    engine = _FakeAIExecutionEngine(_successful_result())
    use_case = GenerateProductDescriptionUseCase(fake_product_intelligence_repository, engine)

    with pytest.raises(ProductIntelligenceNotFoundError):
        await use_case.execute(GenerateProductDescriptionRequestDTO(product_id=uuid4()))


async def test_execute_raises_when_generation_fails(
    fake_product_intelligence_repository, fake_project_repository
):
    project = await fake_project_repository.create("Kitchen Research")
    product = await fake_product_intelligence_repository.create(
        project_id=project.id, research_session_id=None, title="Bamboo Board"
    )
    engine = _FakeAIExecutionEngine(_failed_result("provider unavailable"))
    use_case = GenerateProductDescriptionUseCase(fake_product_intelligence_repository, engine)

    with pytest.raises(AIGenerationFailedError, match="provider unavailable"):
        await use_case.execute(GenerateProductDescriptionRequestDTO(product_id=product.id))

    persisted = await fake_product_intelligence_repository.get_by_id(product.id)
    assert persisted.description is None
