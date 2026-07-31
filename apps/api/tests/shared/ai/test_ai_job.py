import pytest

from app.shared.ai.domain.entities.ai_job import AIJob, AIJobResult, AIJobStatus
from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.exceptions import InvalidAIJobTransitionError


def test_create_starts_pending_with_no_result_or_error():
    job = AIJob.create(capability="generate_title", input_data={"context": "bamboo board"})

    assert job.status == AIJobStatus.PENDING
    assert job.result is None
    assert job.error is None
    assert job.capability == "generate_title"
    assert job.input_data == {"context": "bamboo board"}
    assert job.provider_name is None
    assert job.created_at == job.updated_at


def test_create_defaults_to_no_provider_override():
    job = AIJob.create(capability="generate_title", input_data={})

    assert job.provider_name is None


def test_create_accepts_an_explicit_provider_override():
    job = AIJob.create(
        capability="generate_title", input_data={}, provider_name=AIProviderName.OPENAI
    )

    assert job.provider_name == AIProviderName.OPENAI


def test_start_transitions_pending_to_running():
    job = AIJob.create(capability="generate_title", input_data={})

    running = job.start()

    assert running.status == AIJobStatus.RUNNING
    assert running.id == job.id
    assert job.status == AIJobStatus.PENDING  # original instance is unchanged


def test_start_rejects_a_job_that_is_not_pending():
    job = AIJob.create(capability="generate_title", input_data={}).start()

    with pytest.raises(InvalidAIJobTransitionError):
        job.start()


def test_complete_transitions_running_to_completed_with_a_result():
    job = AIJob.create(capability="generate_title", input_data={}).start()
    result = AIJobResult(output={"title": "Bamboo Board"}, provider=AIProviderName.MOCK)

    completed = job.complete(result)

    assert completed.status == AIJobStatus.COMPLETED
    assert completed.result == result
    assert completed.error is None


def test_complete_rejects_a_job_that_is_not_running():
    job = AIJob.create(capability="generate_title", input_data={})
    result = AIJobResult(output={}, provider=AIProviderName.MOCK)

    with pytest.raises(InvalidAIJobTransitionError):
        job.complete(result)


def test_fail_transitions_running_to_failed_with_an_error():
    job = AIJob.create(capability="generate_title", input_data={}).start()

    failed = job.fail("provider unavailable")

    assert failed.status == AIJobStatus.FAILED
    assert failed.error == "provider unavailable"
    assert failed.result is None


def test_fail_rejects_a_job_that_is_not_running():
    job = AIJob.create(capability="generate_title", input_data={})

    with pytest.raises(InvalidAIJobTransitionError):
        job.fail("too early")


def test_full_lifecycle_pending_running_completed():
    job = AIJob.create(capability="generate_title", input_data={"context": "bamboo board"})
    result = AIJobResult(output={"title": "Bamboo Board"}, provider=AIProviderName.MOCK)

    final = job.start().complete(result)

    assert final.status == AIJobStatus.COMPLETED
    assert final.id == job.id
    assert final.updated_at >= job.created_at
