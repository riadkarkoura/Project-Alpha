from collections.abc import Mapping

import pytest

from app.core.config import settings
from app.shared.ai.application.execution_engine import AIExecutionEngine
from app.shared.ai.application.orchestrator import AIOrchestrator
from app.shared.ai.domain.capabilities.ai_capability import AICapability
from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.ai_job import AIJob
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.exceptions import CapabilityNotFoundError
from app.shared.ai.presentation.dependencies import (
    get_ai_capability_registry,
    get_ai_execution_engine,
    get_ai_orchestrator,
    get_ai_provider_registry,
    get_configured_ai_provider_name,
    get_provider_resolver,
)


class _ProbeCapability(AICapability):
    @property
    def name(self):
        return "probe"

    def build_request(self, input_data: Mapping[str, str]) -> AICompletionRequest:
        return AICompletionRequest(prompt="probe")

    def parse_response(self, response: AICompletionResponse) -> Mapping[str, str]:
        return {"content": response.content}


def test_get_ai_capability_registry_starts_empty():
    """Phase 2 ships the abstraction only - no capability is registered yet."""
    registry = get_ai_capability_registry()

    assert registry.list_names() == []
    with pytest.raises(CapabilityNotFoundError):
        registry.get("generate_title")


def test_get_ai_capability_registry_returns_a_fresh_instance_each_call():
    """No shared global state: registering on one instance must not leak
    into another resolved later."""
    first = get_ai_capability_registry()
    first.register(_ProbeCapability())

    second = get_ai_capability_registry()

    assert second.list_names() == []


def test_get_provider_resolver_uses_the_configured_default(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", AIProviderName.ANTHROPIC)

    resolver = get_provider_resolver(
        provider_registry=get_ai_provider_registry(),
        default_provider_name=get_configured_ai_provider_name(),
    )
    job = AIJob.create(capability="probe", input_data={})

    provider = resolver.resolve(job)

    assert provider.name == AIProviderName.ANTHROPIC


def test_get_ai_orchestrator_returns_a_stateless_orchestrator():
    orchestrator = get_ai_orchestrator()

    assert isinstance(orchestrator, AIOrchestrator)


def test_get_ai_execution_engine_wires_a_usable_engine():
    engine = get_ai_execution_engine(
        capability_registry=get_ai_capability_registry(),
        provider_resolver=get_provider_resolver(
            provider_registry=get_ai_provider_registry(),
            default_provider_name=get_configured_ai_provider_name(),
        ),
        orchestrator=get_ai_orchestrator(),
    )

    assert isinstance(engine, AIExecutionEngine)


async def test_get_ai_execution_engine_uses_the_configured_default_provider(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", AIProviderName.ANTHROPIC)
    capability_registry = get_ai_capability_registry()
    capability_registry.register(_ProbeCapability())

    engine = get_ai_execution_engine(
        capability_registry=capability_registry,
        provider_resolver=get_provider_resolver(
            provider_registry=get_ai_provider_registry(),
            default_provider_name=get_configured_ai_provider_name(),
        ),
        orchestrator=get_ai_orchestrator(),
    )
    job = AIJob.create(capability="probe", input_data={})

    result = await engine.execute(job)

    assert result.is_success
    assert result.job.result is not None
    assert result.job.result.provider == AIProviderName.ANTHROPIC
