from fastapi import Depends

from app.core.config import settings
from app.shared.ai.application.capability_registry import AICapabilityRegistry
from app.shared.ai.application.execution_engine import AIExecutionEngine
from app.shared.ai.application.orchestrator import AIOrchestrator
from app.shared.ai.application.provider_registry import AIProviderRegistry
from app.shared.ai.application.provider_resolver import ProviderResolver
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.providers.ai_provider import AIProvider
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
    """Direct access to the configured default provider, with no job
    context. Most callers should prefer `Depends(get_ai_execution_engine)`;
    this exists for the rare case that needs the provider itself and has no
    AIJob to reason about."""
    return registry.get(provider_name)


def get_ai_capability_registry() -> AICapabilityRegistry:
    """Composition root for AI capabilities.

    Empty in Phase 2: no capability is implemented yet, only the
    abstraction. Future sprints register real capabilities here the same
    way get_ai_provider_registry() registers providers - AIExecutionEngine
    and every other caller stay unchanged.
    """
    return AICapabilityRegistry()


def get_provider_resolver(
    provider_registry: AIProviderRegistry = Depends(get_ai_provider_registry),  # noqa: B008
    default_provider_name: AIProviderName = Depends(get_configured_ai_provider_name),  # noqa: B008
) -> ProviderResolver:
    return ProviderResolver(provider_registry, default_provider_name)


def get_ai_orchestrator() -> AIOrchestrator:
    """AIOrchestrator is stateless (pure execution mechanics over
    already-resolved collaborators), so there is nothing to inject."""
    return AIOrchestrator()


def get_ai_execution_engine(
    capability_registry: AICapabilityRegistry = Depends(  # noqa: B008
        get_ai_capability_registry
    ),
    provider_resolver: ProviderResolver = Depends(get_provider_resolver),  # noqa: B008
    orchestrator: AIOrchestrator = Depends(get_ai_orchestrator),  # noqa: B008
) -> AIExecutionEngine:
    """The one dependency any future AI-driven use case should need:
    `Depends(get_ai_execution_engine)`. It never imports a concrete
    capability or provider, and never reads Settings.ai_provider itself -
    swapping the configured provider, adding a provider, or adding a
    capability never touches a caller of this dependency."""
    return AIExecutionEngine(capability_registry, provider_resolver, orchestrator)
