from fastapi import Depends

from app.core.config import settings
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.providers.ai_provider import AIProvider
from app.shared.ai.infrastructure.provider_registry import AIProviderRegistry
from app.shared.ai.infrastructure.providers.anthropic_provider import AnthropicProvider
from app.shared.ai.infrastructure.providers.mock_ai_provider import MockAIProvider
from app.shared.ai.infrastructure.providers.openai_provider import OpenAIProvider


def get_ai_provider_registry() -> AIProviderRegistry:
    """Composition root for AI providers.

    Constructed fresh on every call (no module-level singleton instances):
    providers are cheap/stateless, and this keeps the registry trivially
    overridable in tests without any shared global state to reset.
    """
    return AIProviderRegistry(
        {
            AIProviderName.MOCK: MockAIProvider(),
            AIProviderName.OPENAI: OpenAIProvider(),
            AIProviderName.ANTHROPIC: AnthropicProvider(),
        }
    )


def get_configured_ai_provider_name() -> AIProviderName:
    return settings.ai_provider


def get_ai_provider(
    registry: AIProviderRegistry = Depends(get_ai_provider_registry),  # noqa: B008
    provider_name: AIProviderName = Depends(get_configured_ai_provider_name),  # noqa: B008
) -> AIProvider:
    """The only thing business logic should depend on: `Depends(get_ai_provider)`.

    Callers never import a concrete provider class or read
    `settings.ai_provider` themselves - swapping the configured provider, or
    adding a new one, never touches a caller.
    """
    return registry.get(provider_name)
