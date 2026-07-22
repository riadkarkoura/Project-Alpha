from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateProjectRequestDTO:
    name: str


@dataclass(frozen=True)
class CreateProjectResponseDTO:
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime
