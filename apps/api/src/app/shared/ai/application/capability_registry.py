from app.shared.ai.domain.capabilities.ai_capability import AICapability
from app.shared.ai.domain.entities.capability_name import CapabilityName
from app.shared.ai.domain.exceptions import CapabilityNotFoundError


class AICapabilityRegistry:
    """Resolves an AICapability by name.

    Lives in application/ for the same reason AIProviderRegistry does: it
    only manipulates the AICapability abstraction, never a concrete
    implementation. Mirrors AIProviderRegistry deliberately - the same
    lookup/registration shape for both axes (provider, capability) the
    execution engine resolves. Adding a new capability means registering
    one more entry where the registry is built - this class is unchanged.
    No capability is registered here in Phase 2; the registry starts empty
    until real capabilities are implemented.
    """

    def __init__(self, capabilities: dict[CapabilityName, AICapability] | None = None) -> None:
        self._capabilities: dict[CapabilityName, AICapability] = dict(capabilities or {})

    def get(self, name: CapabilityName) -> AICapability:
        try:
            return self._capabilities[name]
        except KeyError:
            raise CapabilityNotFoundError(f"No AI capability registered for '{name}'.") from None

    def register(self, capability: AICapability) -> None:
        self._capabilities[capability.name] = capability

    def list_names(self) -> list[CapabilityName]:
        return sorted(self._capabilities)
