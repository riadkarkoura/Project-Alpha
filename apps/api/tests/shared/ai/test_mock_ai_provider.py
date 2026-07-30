from app.shared.ai.domain.entities.ai_completion import AICompletionRequest
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.infrastructure.providers.mock_ai_provider import MockAIProvider


async def test_name_is_mock():
    provider = MockAIProvider()

    assert provider.name == AIProviderName.MOCK


async def test_complete_returns_a_response_tagged_with_the_mock_provider():
    provider = MockAIProvider()

    response = await provider.complete(AICompletionRequest(prompt="Describe a bamboo board."))

    assert response.provider == AIProviderName.MOCK
    assert response.content


async def test_complete_is_deterministic_for_the_same_prompt():
    provider = MockAIProvider()
    request = AICompletionRequest(prompt="Describe a bamboo board.")

    first = await provider.complete(request)
    second = await provider.complete(request)

    assert first == second


async def test_complete_reflects_the_prompt_in_the_content():
    provider = MockAIProvider()

    response = await provider.complete(AICompletionRequest(prompt="unique-marker-xyz"))

    assert "unique-marker-xyz" in response.content
