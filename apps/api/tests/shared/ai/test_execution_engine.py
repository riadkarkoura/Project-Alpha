from collections.abc import Mapping

import pytest

from app.shared.ai.application.capability_registry import AICapabilityRegistry
from app.shared.ai.application.execution_engine import AIExecutionEngine
from app.shared.ai.application.orchestrator import AIOrchestrator
from app.shared.ai.application.provider_registry import AIProviderRegistry
from app.shared.ai.application.provider_resolver import ProviderResolver
from app.shared.ai.domain.capabilities.ai_capability import AICapability
from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.ai_job import AIJob
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.exceptions import AIProviderNotConfiguredError, CapabilityNotFoundError
from app.shared.ai.infrastructure.providers.mock_ai_provider import MockAIProvider
from app.shared.ai.infrastructure.providers.openai_provider import OpenAIProvider


class _EchoCapability(AICapability):
    @property
    def name(self):
        return "echo"

    def build_request(self, input_data: Mapping[str, str]) -> AICompletionRequest:
        return AICompletionRequest(prompt=input_data.get("text", ""))

    def parse_response(self, response: AICompletionResponse) -> Mapping[str, str]:
        return {"echoed": response.content}


def _engine(
    capabilities: dict | None = None,
    providers: dict | None = None,
    default_provider_name: AIProviderName = AIProviderName.MOCK,
) -> AIExecutionEngine:
    capability_registry = AICapabilityRegistry(capabilities or {})
    provider_registry = AIProviderRegistry(providers or {})
    resolver = ProviderResolver(provider_registry, default_provider_name)
    return AIExecutionEngine(capability_registry, resolver, AIOrchestrator())


async def test_execute_returns_a_successful_result_using_the_mock_provider():
    engine = _engine(
        capabilities={"echo": _EchoCapability()}, providers={AIProviderName.MOCK: MockAIProvider()}
    )
    job = AIJob.create(capability="echo", input_data={"text": "hello"})

    result = await engine.execute(job)

    assert result.is_success
    assert result.error is None
    assert result.output == {"echoed": "[mock completion for prompt: 'hello']"}
    assert result.job.result is not None
    assert result.job.result.provider == AIProviderName.MOCK


async def test_execute_raises_when_the_jobs_capability_is_not_registered():
    engine = _engine(capabilities={}, providers={AIProviderName.MOCK: MockAIProvider()})
    job = AIJob.create(capability="unknown", input_data={})

    with pytest.raises(CapabilityNotFoundError):
        await engine.execute(job)


async def test_execute_raises_when_no_provider_is_configured():
    engine = _engine(capabilities={"echo": _EchoCapability()}, providers={})
    job = AIJob.create(capability="echo", input_data={"text": "hello"})

    with pytest.raises(AIProviderNotConfiguredError):
        await engine.execute(job)


async def test_execute_uses_the_configured_default_provider():
    engine = _engine(
        capabilities={"echo": _EchoCapability()},
        providers={AIProviderName.MOCK: MockAIProvider(), AIProviderName.OPENAI: OpenAIProvider()},
        default_provider_name=AIProviderName.MOCK,
    )
    job = AIJob.create(capability="echo", input_data={"text": "hello"})

    result = await engine.execute(job)

    assert result.job.result is not None
    assert result.job.result.provider == AIProviderName.MOCK


async def test_execute_honors_a_per_job_provider_override():
    engine = _engine(
        capabilities={"echo": _EchoCapability()},
        providers={AIProviderName.MOCK: MockAIProvider(), AIProviderName.OPENAI: OpenAIProvider()},
        default_provider_name=AIProviderName.MOCK,
    )
    job = AIJob.create(
        capability="echo", input_data={"text": "hello"}, provider_name=AIProviderName.OPENAI
    )

    result = await engine.execute(job)

    assert result.job.result is not None
    assert result.job.result.provider == AIProviderName.OPENAI


async def test_execute_never_needs_a_concrete_provider_or_capability_import():
    """Architectural regression guard: this test file only ever constructs
    AIExecutionEngine from registries/resolver/orchestrator - it never
    reaches into a concrete provider from inside the engine's own code."""
    import inspect

    from app.shared.ai.application import execution_engine as module

    source = inspect.getsource(module)
    assert "MockAIProvider" not in source
    assert "OpenAIProvider" not in source
    assert "AnthropicProvider" not in source
