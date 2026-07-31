from collections.abc import Mapping

from app.shared.ai.application.orchestrator import AIOrchestrator
from app.shared.ai.domain.capabilities.ai_capability import AICapability
from app.shared.ai.domain.entities.ai_completion import AICompletionRequest, AICompletionResponse
from app.shared.ai.domain.entities.ai_job import AIJob, AIJobStatus
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.providers.ai_provider import AIProvider


class _EchoCapability(AICapability):
    """A fake capability - proves the orchestrator only depends on the
    AICapability interface, never on a concrete implementation."""

    @property
    def name(self):
        return "echo"

    def build_request(self, input_data: Mapping[str, str]) -> AICompletionRequest:
        return AICompletionRequest(prompt=input_data.get("text", ""))

    def parse_response(self, response: AICompletionResponse) -> Mapping[str, str]:
        return {"echoed": response.content}


class _FakeProvider(AIProvider):
    """A fake provider - proves the orchestrator only depends on the
    AIProvider interface, never on a concrete implementation."""

    def __init__(self, provider_name: AIProviderName, error: Exception | None = None) -> None:
        self._name = provider_name
        self._error = error

    @property
    def name(self) -> AIProviderName:
        return self._name

    async def complete(self, request: AICompletionRequest) -> AICompletionResponse:
        if self._error is not None:
            raise self._error
        return AICompletionResponse(content=f"response to: {request.prompt}", provider=self._name)


async def test_run_executes_a_job_to_completion():
    orchestrator = AIOrchestrator()
    job = AIJob.create(capability="echo", input_data={"text": "hello"})

    result_job = await orchestrator.run(job, _EchoCapability(), _FakeProvider(AIProviderName.MOCK))

    assert result_job.status == AIJobStatus.COMPLETED
    assert result_job.result is not None
    assert result_job.result.output == {"echoed": "response to: hello"}
    assert result_job.result.provider == AIProviderName.MOCK
    assert result_job.id == job.id


async def test_run_does_not_mutate_the_original_job():
    orchestrator = AIOrchestrator()
    job = AIJob.create(capability="echo", input_data={"text": "hello"})

    await orchestrator.run(job, _EchoCapability(), _FakeProvider(AIProviderName.MOCK))

    assert job.status == AIJobStatus.PENDING


async def test_run_marks_the_job_failed_when_the_provider_raises():
    orchestrator = AIOrchestrator()
    job = AIJob.create(capability="echo", input_data={"text": "hello"})
    failing_provider = _FakeProvider(AIProviderName.MOCK, error=RuntimeError("provider is down"))

    result_job = await orchestrator.run(job, _EchoCapability(), failing_provider)

    assert result_job.status == AIJobStatus.FAILED
    assert result_job.error == "provider is down"
    assert result_job.result is None


async def test_run_marks_the_job_failed_when_the_capability_raises():
    class _BrokenCapability(_EchoCapability):
        def parse_response(self, response: AICompletionResponse) -> Mapping[str, str]:
            raise ValueError("cannot parse this response")

    orchestrator = AIOrchestrator()
    job = AIJob.create(capability="echo", input_data={"text": "hello"})

    provider = _FakeProvider(AIProviderName.MOCK)
    result_job = await orchestrator.run(job, _BrokenCapability(), provider)

    assert result_job.status == AIJobStatus.FAILED
    assert result_job.error == "cannot parse this response"


async def test_run_passes_the_jobs_input_data_to_the_capability():
    received: dict[str, Mapping[str, str]] = {}

    class _CapturingCapability(_EchoCapability):
        def build_request(self, input_data: Mapping[str, str]) -> AICompletionRequest:
            received["input_data"] = input_data
            return super().build_request(input_data)

    orchestrator = AIOrchestrator()
    job = AIJob.create(capability="echo", input_data={"text": "hello", "tone": "formal"})

    await orchestrator.run(job, _CapturingCapability(), _FakeProvider(AIProviderName.MOCK))

    assert received["input_data"] == {"text": "hello", "tone": "formal"}
