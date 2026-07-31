from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.exceptions import AIProviderNotConfiguredError
from app.shared.ai.domain.providers.ai_provider import AIProvider


class AIProviderRegistry:
    """Resolves an AIProvider by name.

    Lives in application/, not infrastructure/: this class only ever
    touches the AIProvider abstraction (a dict lookup over an interface
    type), never a concrete SDK or I/O call - registering/looking up
    providers is coordination logic, not infrastructure. The concrete
    provider classes it gets populated with at the composition root
    (presentation/dependencies.py) are what belongs in infrastructure/.

    Adding a new provider means registering one more entry where the
    registry is constructed - this class and every caller of `get()` are
    unchanged.
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
