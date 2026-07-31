from collections.abc import Mapping
from dataclasses import dataclass

from app.shared.ai.domain.entities.ai_job import AIJob, AIJobStatus


@dataclass(frozen=True)
class AIExecutionResult:
    """The normalized outcome AIExecutionEngine.execute() returns.

    A thin read view over the underlying AIJob: future use cases consume
    this (is_success / output / error) without needing to know AIJob's
    status enum or its result/error split. AIJob itself stays the rich
    domain aggregate - the one a future AIJobRepository would persist -
    while this is purely a caller-facing convenience.

    Known placement debt (intentional, not yet actioned): this type is
    conceptually an application-layer boundary result - nothing in the
    domain produces or consumes it, only AIExecutionEngine does, and only
    to hand a caller-friendly shape back to a use case. It lives here today
    because it has no infrastructure dependency and mirrors how response
    DTOs are modeled elsewhere in this codebase, not because domain/ is its
    correct long-term home. Move it to application/ (alongside
    execution_engine.py) once that layer's boundary types grow enough to
    make the distinction matter - a one-file, no-behavior-change move.
    Left as-is for now rather than moved speculatively.
    """

    job: AIJob

    @property
    def is_success(self) -> bool:
        return self.job.status == AIJobStatus.COMPLETED

    @property
    def output(self) -> Mapping[str, str] | None:
        return self.job.result.output if self.job.result else None

    @property
    def error(self) -> str | None:
        return self.job.error
