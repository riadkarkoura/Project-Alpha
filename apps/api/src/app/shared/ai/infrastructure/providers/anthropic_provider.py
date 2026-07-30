from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.providers.ai_provider import AIProvider


class AnthropicProvider(AIProvider):
    """Placeholder for a future Anthropic integration.

    Deliberately does not import or call the Anthropic SDK - Phase 1 builds
    the contract only. `api_key` is accepted so the configuration/DI path is
    already shaped for a real client later; it is unused today.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self._api_key = api_key

    @property
    def name(self) -> AIProviderName:
        return AIProviderName.ANTHROPIC

    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        return AICompletionResponse(
            content="[Anthropic provider placeholder - integration not yet implemented]",
            provider=AIProviderName.ANTHROPIC,
            model=None,
        )
