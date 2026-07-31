from app.shared.ai.application.provider_registry import AIProviderRegistry
from app.shared.ai.domain.entities.ai_job import AIJob
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.providers.ai_provider import AIProvider


class ProviderResolver:
    """Decides which AIProvider should run a given job.

    Separated from AIProviderRegistry on purpose: the registry only answers
    "give me the provider registered under this name"; the resolver answers
    "which name should this job use" - a policy question. Today that policy
    is trivial (an explicit per-job override, else the configured default),
    but this is deliberately the one seam where future provider fallback and
    model routing logic will grow. AIExecutionEngine calls `resolve()` and
    never needs to change when that policy does.
    """

    def __init__(
        self, provider_registry: AIProviderRegistry, default_provider_name: AIProviderName
    ) -> None:
        self._provider_registry = provider_registry
        self._default_provider_name = default_provider_name

    def resolve(self, job: AIJob) -> AIProvider:
        provider_name = job.provider_name or self._default_provider_name
        return self._provider_registry.get(provider_name)
