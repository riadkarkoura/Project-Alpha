import dataclasses
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.shared.ai.domain.entities.ai_provider_name import AIProviderName
from app.shared.ai.domain.entities.capability_name import CapabilityName
from app.shared.ai.domain.exceptions import InvalidAIJobTransitionError


class AIJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class AIJobResult:
    """Normalized output of a completed job - the same shape regardless of
    which capability or provider produced it."""

    output: Mapping[str, str]
    provider: AIProviderName
    model: str | None = None


@dataclass(frozen=True)
class AIJob:
    """One AI execution request.

    Deliberately generic: `capability` is an identifier (not a product
    concept), and `input_data` is a flat string map the resolved capability
    is responsible for interpreting. Nothing here references Product
    Intelligence, prompts, or any specific AI task.

    The pending/running/completed/failed lifecycle is shaped to support
    both synchronous execution (all four transitions happen in one call, as
    the Phase 2 orchestrator does today) and a future asynchronous worker
    (a job persisted as `pending`, picked up later, transitioned over time -
    no persistence layer exists yet, but this shape does not preclude one).
    """

    id: UUID
    capability: CapabilityName
    input_data: Mapping[str, str]
    provider_name: AIProviderName | None
    status: AIJobStatus
    result: AIJobResult | None
    error: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        capability: CapabilityName,
        input_data: Mapping[str, str],
        provider_name: AIProviderName | None = None,
    ) -> "AIJob":
        now = datetime.now(UTC)
        return cls(
            id=uuid4(),
            capability=capability,
            input_data=dict(input_data),
            provider_name=provider_name,
            status=AIJobStatus.PENDING,
            result=None,
            error=None,
            created_at=now,
            updated_at=now,
        )

    def start(self) -> "AIJob":
        self._require_status(AIJobStatus.PENDING, action="start")
        return dataclasses.replace(
            self, status=AIJobStatus.RUNNING, updated_at=datetime.now(UTC)
        )

    def complete(self, result: AIJobResult) -> "AIJob":
        self._require_status(AIJobStatus.RUNNING, action="complete")
        return dataclasses.replace(
            self,
            status=AIJobStatus.COMPLETED,
            result=result,
            updated_at=datetime.now(UTC),
        )

    def fail(self, error: str) -> "AIJob":
        self._require_status(AIJobStatus.RUNNING, action="fail")
        return dataclasses.replace(
            self,
            status=AIJobStatus.FAILED,
            error=error,
            updated_at=datetime.now(UTC),
        )

    def _require_status(self, expected: AIJobStatus, *, action: str) -> None:
        if self.status != expected:
            raise InvalidAIJobTransitionError(
                f"Cannot {action} job {self.id}: expected status {expected}, "
                f"got {self.status}."
            )
