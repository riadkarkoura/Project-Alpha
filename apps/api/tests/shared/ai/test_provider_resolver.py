from app.shared.ai.application.provider_registry import AIProviderRegistry
from app.shared.ai.application.provider_resolver import ProviderResolver
from app.shared.ai.domain.entities.ai_job import AIJob
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.infrastructure.providers.mock_ai_provider import MockAIProvider
from app.shared.ai.infrastructure.providers.openai_provider import OpenAIProvider


def _registry() -> AIProviderRegistry:
    return AIProviderRegistry(
        {AIProviderName.MOCK: MockAIProvider(), AIProviderName.OPENAI: OpenAIProvider()}
    )


def test_resolve_uses_the_default_when_the_job_has_no_override():
    resolver = ProviderResolver(_registry(), default_provider_name=AIProviderName.MOCK)
    job = AIJob.create(capability="echo", input_data={})

    provider = resolver.resolve(job)

    assert provider.name == AIProviderName.MOCK


def test_resolve_uses_the_jobs_provider_override_when_present():
    resolver = ProviderResolver(_registry(), default_provider_name=AIProviderName.MOCK)
    job = AIJob.create(capability="echo", input_data={}, provider_name=AIProviderName.OPENAI)

    provider = resolver.resolve(job)

    assert provider.name == AIProviderName.OPENAI


def test_resolve_delegates_lookup_to_the_registry():
    """The resolver decides *which name* to use; the registry still owns
    *how that name becomes an instance* - resolve() must not bypass it."""
    registry = _registry()
    mock_provider = registry.get(AIProviderName.MOCK)
    resolver = ProviderResolver(registry, default_provider_name=AIProviderName.MOCK)
    job = AIJob.create(capability="echo", input_data={})

    provider = resolver.resolve(job)

    assert provider is mock_provider
