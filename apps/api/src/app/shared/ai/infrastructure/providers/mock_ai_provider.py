from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.providers.ai_provider import AIProvider


class MockAIProvider(AIProvider):
    """Deterministic placeholder - no external calls.

    The safe default provider (see Settings.ai_provider) until a real
    integration is explicitly configured.
    """

    @property
    def name(self) -> AIProviderName:
        return AIProviderName.MOCK

    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        return AICompletionResponse(
            content=f"[mock completion for prompt: {request.prompt[:50]!r}]",
            provider=AIProviderName.MOCK,
            model="mock-1",
        )
