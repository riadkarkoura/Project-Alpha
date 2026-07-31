from app.shared.ai.application.capability_registry import AICapabilityRegistry
from app.shared.ai.application.orchestrator import AIOrchestrator
from app.shared.ai.application.provider_resolver import ProviderResolver
from app.shared.ai.domain.entities.ai_execution_result import AIExecutionResult
from app.shared.ai.domain.entities.ai_job import AIJob


class AIExecutionEngine:
    """The single entry point every AI-driven use case should depend on.

    "Use cases communicate only with the Execution Engine": this is that
    boundary. `execute()` resolves the job's capability and provider, runs
    it via AIOrchestrator, and returns a normalized AIExecutionResult - the
    engine never depends on a concrete capability or provider itself.

    This is deliberately where AIJob persistence and asynchronous execution
    will be introduced later (e.g. persist `job` as pending via a future
    AIJobRepository before running it, or hand off to a background worker
    instead of awaiting AIOrchestrator inline). That change touches only
    this method's body - its signature, and every caller's code, stays the
    same, which is the whole point of having this class sit in front of
    AIOrchestrator rather than exposing the orchestrator directly.
    """

    def __init__(
        self,
        capability_registry: AICapabilityRegistry,
        provider_resolver: ProviderResolver,
        orchestrator: AIOrchestrator,
    ) -> None:
        self._capability_registry = capability_registry
        self._provider_resolver = provider_resolver
        self._orchestrator = orchestrator

    async def execute(self, job: AIJob) -> AIExecutionResult:
        capability = self._capability_registry.get(job.capability)
        provider = self._provider_resolver.resolve(job)

        final_job = await self._orchestrator.run(job, capability, provider)
        return AIExecutionResult(job=final_job)
