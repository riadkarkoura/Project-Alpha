import pytest

from app.core.config import settings
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.infrastructure.providers.anthropic_provider import AnthropicProvider
from app.shared.ai.infrastructure.providers.mock_ai_provider import MockAIProvider
from app.shared.ai.infrastructure.providers.openai_provider import OpenAIProvider
from app.shared.ai.presentation.dependencies import (
    get_ai_provider,
    get_ai_provider_registry,
    get_configured_ai_provider_name,
)


def test_get_ai_provider_registry_contains_every_known_provider():
    registry = get_ai_provider_registry()

    assert isinstance(registry.get(AIProviderName.MOCK), MockAIProvider)
    assert isinstance(registry.get(AIProviderName.OPENAI), OpenAIProvider)
    assert isinstance(registry.get(AIProviderName.ANTHROPIC), AnthropicProvider)


def test_get_configured_ai_provider_name_reflects_settings(monkeypatch):
    monkeypatch.setattr(settings, "ai_provider", AIProviderName.ANTHROPIC)

    assert get_configured_ai_provider_name() == AIProviderName.ANTHROPIC


@pytest.mark.parametrize(
    ("configured_name", "expected_type"),
    [
        (AIProviderName.MOCK, MockAIProvider),
        (AIProviderName.OPENAI, OpenAIProvider),
        (AIProviderName.ANTHROPIC, AnthropicProvider),
    ],
)
def test_get_ai_provider_resolves_the_configured_provider(
    monkeypatch, configured_name, expected_type
):
    monkeypatch.setattr(settings, "ai_provider", configured_name)

    provider = get_ai_provider(
        registry=get_ai_provider_registry(),
        provider_name=get_configured_ai_provider_name(),
    )

    assert isinstance(provider, expected_type)


def test_get_ai_provider_never_requires_the_caller_to_know_the_concrete_provider(monkeypatch):
    """Regression guard for the core promise of this architecture: swapping
    the configured provider changes what `get_ai_provider` returns without
    the caller importing or naming any concrete provider class."""
    monkeypatch.setattr(settings, "ai_provider", AIProviderName.OPENAI)
    provider_a = get_ai_provider(
        registry=get_ai_provider_registry(), provider_name=get_configured_ai_provider_name()
    )

    monkeypatch.setattr(settings, "ai_provider", AIProviderName.ANTHROPIC)
    provider_b = get_ai_provider(
        registry=get_ai_provider_registry(), provider_name=get_configured_ai_provider_name()
    )

    assert provider_a.name != provider_b.name
