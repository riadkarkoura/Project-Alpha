from app.features.product_intelligence.presentation.api.dependencies import (
    get_product_intelligence_ai_execution_engine,
)
from app.shared.ai.domain.entities.ai_job import AIJob
from app.shared.ai.presentation.dependencies import (
    get_ai_orchestrator,
    get_ai_provider_registry,
    get_configured_ai_provider_name,
    get_provider_resolver,
)


async def test_the_real_composed_engine_resolves_the_capability_and_uses_mock_provider():
    """Proves the actual DI wiring (not a fake): the capability
    product_intelligence registers is discoverable, and execution runs
    through MockProvider end-to-end - no fakes/mocks in this test."""
    engine = get_product_intelligence_ai_execution_engine(
        provider_resolver=get_provider_resolver(
            provider_registry=get_ai_provider_registry(),
            default_provider_name=get_configured_ai_provider_name(),
        ),
        orchestrator=get_ai_orchestrator(),
    )
    job = AIJob.create(
        capability="generate_product_description",
        input_data={"title": "Bamboo Board", "subtitle": "", "category": "Kitchen"},
    )

    result = await engine.execute(job)

    assert result.is_success
    assert result.output is not None
    assert "mock completion" in result.output["description"]
    assert result.job.result is not None
    assert result.job.result.provider.value == "mock"
