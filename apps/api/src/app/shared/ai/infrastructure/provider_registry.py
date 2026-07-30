from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.exceptions import AIProviderNotConfiguredError
from app.shared.ai.domain.providers.ai_provider import AIProvider


class AIProviderRegistry:
    """Resolves an AIProvider by name.

    Adding a new provider means registering one more entry where the
    registry is constructed (see presentation/dependencies.py) - this class
    and every caller of `get()` are unchanged.
    """

    def __init__(self, providers: dict[AIProviderName, AIProvider]) -> None:
        self._providers = dict(providers)

    def get(self, name: AIProviderName) -> AIProvider:
        try:
            return self._providers[name]
        except KeyError:
            raise AIProviderNotConfiguredError(f"No AI provider registered for '{name}'.") from None

    def register(self, provider: AIProvider) -> None:
        self._providers[provider.name] = provider
