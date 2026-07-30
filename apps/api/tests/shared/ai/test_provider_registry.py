import pytest

from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.exceptions import AIProviderNotConfiguredError
from app.shared.ai.domain.providers.ai_provider import AIProvider
from app.shared.ai.infrastructure.provider_registry import AIProviderRegistry
from app.shared.ai.infrastructure.providers.mock_ai_provider import MockAIProvider


class _FakeProvider(AIProvider):
    def __init__(self, provider_name: AIProviderName) -> None:
        self._name = provider_name

    @property
    def name(self) -> AIProviderName:
        return self._name

    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        return AICompletionResponse(content="fake", provider=self._name)


def test_get_resolves_a_registered_provider():
    mock_provider = MockAIProvider()
    registry = AIProviderRegistry({AIProviderName.MOCK: mock_provider})

    assert registry.get(AIProviderName.MOCK) is mock_provider


def test_get_raises_for_an_unregistered_provider():
    registry = AIProviderRegistry({})

    with pytest.raises(AIProviderNotConfiguredError):
        registry.get(AIProviderName.OPENAI)


def test_register_adds_a_new_provider_without_touching_existing_ones():
    mock_provider = MockAIProvider()
    registry = AIProviderRegistry({AIProviderName.MOCK: mock_provider})
    new_provider = _FakeProvider(AIProviderName.ANTHROPIC)

    registry.register(new_provider)

    assert registry.get(AIProviderName.ANTHROPIC) is new_provider
    assert registry.get(AIProviderName.MOCK) is mock_provider


def test_register_replaces_an_existing_provider_for_the_same_name():
    registry = AIProviderRegistry({AIProviderName.MOCK: MockAIProvider()})
    replacement = _FakeProvider(AIProviderName.MOCK)

    registry.register(replacement)

    assert registry.get(AIProviderName.MOCK) is replacement


def test_constructor_copies_the_input_dict_so_external_mutation_does_not_leak_in():
    providers = {AIProviderName.MOCK: MockAIProvider()}
    registry = AIProviderRegistry(providers)

    providers[AIProviderName.OPENAI] = MockAIProvider()

    with pytest.raises(AIProviderNotConfiguredError):
        registry.get(AIProviderName.OPENAI)
