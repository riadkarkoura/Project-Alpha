from app.shared.ai.domain.capabilities.ai_capability import AICapability
from app.shared.ai.domain.entities.ai_job import AIJob, AIJobResult
from app.shared.ai.domain.providers.ai_provider import AIProvider


class AIOrchestrator:
    """Pure execution mechanics for one already-resolved AI job.

    Command Pattern: `run()` executes an AIJob (the command) against an
    already-resolved AICapability and AIProvider (the receivers) without
    knowing how either was chosen, or what happens to the result afterward.
    Resolution (which capability, which provider) is deliberately not this
    class's job - see AIExecutionEngine, which resolves both and delegates
    here. That split is what keeps this class stateless and trivial to
    test in isolation from registries/config entirely.

    A failure *during* execution (capability/provider already resolved)
    is captured on the job via `AIJob.fail()`, since that's a legitimate
    execution outcome, not a programmer error - unlike resolution failures,
    which are raised by the registries before `run()` is ever called.
    """

    async def run(self, job: AIJob, capability: AICapability, provider: AIProvider) -> AIJob:
        running_job = job.start()

        try:
            request = capability.build_request(running_job.input_data)
            response = await provider.complete(request)
            output = capability.parse_response(response)
        except Exception as exc:
            # Deliberately broad: any capability/provider failure becomes a
            # failed job, not a raised exception, once execution has begun.
            return running_job.fail(str(exc))

        result = AIJobResult(output=output, provider=response.provider, model=response.model)
        return running_job.complete(result)
