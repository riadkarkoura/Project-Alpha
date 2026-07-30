import pytest

from app.shared.ai.domain.entities.ai_completion import AICompletionRequest
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.infrastructure.providers.anthropic_provider import AnthropicProvider
from app.shared.ai.infrastructure.providers.openai_provider import OpenAIProvider


@pytest.mark.parametrize(
    ("provider_cls", "expected_name"),
    [
        (OpenAIProvider, AIProviderName.OPENAI),
        (AnthropicProvider, AIProviderName.ANTHROPIC),
    ],
)
async def test_placeholder_provider_reports_its_name(provider_cls, expected_name):
    provider = provider_cls()

    assert provider.name == expected_name


@pytest.mark.parametrize("provider_cls", [OpenAIProvider, AnthropicProvider])
async def test_placeholder_provider_returns_a_placeholder_response(provider_cls):
    provider = provider_cls()

    response = await provider.complete(AICompletionRequest(prompt="Anything"))

    assert response.provider == provider.name
    assert "placeholder" in response.content.lower()


@pytest.mark.parametrize("provider_cls", [OpenAIProvider, AnthropicProvider])
async def test_placeholder_provider_accepts_an_optional_api_key_without_using_it(provider_cls):
    provider = provider_cls(api_key="not-a-real-key")

    response = await provider.complete(AICompletionRequest(prompt="Anything"))

    assert response.provider == provider.name
