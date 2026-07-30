from dataclasses import dataclass

from app.shared.ai.domain.entities.ai_provider_name import AIProviderName


@dataclass(frozen=True)
class AICompletionRequest:
    """Generic contract for a single-turn AI completion.

    Deliberately business-agnostic: no product/SEO/pricing concepts here.
    Future capabilities (title generation, SEO copy, etc.) are application-
    layer callers that build one of these and hand it to an AIProvider;
    this shape must not grow business-specific fields to support them.
    """

    prompt: str
    system_prompt: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None


@dataclass(frozen=True)
class AICompletionResponse:
    content: str
    provider: AIProviderName
    model: str | None = None
