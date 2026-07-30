from abc import ABC, abstractmethod

from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName


class AIProvider(ABC):
    """Port every AI/LLM backend must implement (Strategy Pattern).

    Business logic depends only on this interface, never on a concrete
    provider or a vendor SDK. Future capabilities (title generation, SEO
    copy, etc.) are built as callers of `complete()`, not as new methods
    here - that is what keeps this contract stable as capabilities grow.
    """

    @property
    @abstractmethod
    def name(self) -> AIProviderName:
        raise NotImplementedError

    @abstractmethod
    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        raise NotImplementedError
