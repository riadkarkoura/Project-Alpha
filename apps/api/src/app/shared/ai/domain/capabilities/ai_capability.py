from abc import ABC, abstractmethod
from collections.abc import Mapping

from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.capability_name import CapabilityName


class AICapability(ABC):
    """One discrete AI task (Generate Title, Generate SEO, Translate, ...).

    A capability is the translation boundary between a generic AIJob and
    the provider-facing completion contract: it decides what prompt a task
    needs and how to interpret the provider's response, so neither the
    AIExecutionEngine/AIOrchestrator nor any AIProvider needs to know what
    the task is.

    No concrete capability is implemented in this phase - only the
    abstraction. `build_request`/`parse_response` are where future prompt
    engineering will live, not here.
    """

    @property
    @abstractmethod
    def name(self) -> CapabilityName:
        raise NotImplementedError

    @abstractmethod
    def build_request(self, input_data: Mapping[str, str]) -> AICompletionRequest:
        raise NotImplementedError

    @abstractmethod
    def parse_response(self, response: AICompletionResponse) -> Mapping[str, str]:
        raise NotImplementedError
