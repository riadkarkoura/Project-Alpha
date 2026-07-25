from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSessionStatus,
)


@dataclass(frozen=True)
class CreateResearchSessionRequestDTO:
    project_id: UUID
    marketplace: Marketplace


@dataclass(frozen=True)
class ResearchSessionDTO:
    id: UUID
    project_id: UUID
    marketplace: Marketplace
    status: ResearchSessionStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ListResearchSessionsRequestDTO:
    project_id: UUID
