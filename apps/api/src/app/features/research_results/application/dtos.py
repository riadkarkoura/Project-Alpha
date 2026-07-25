from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateResearchResultRequestDTO:
    research_session_id: UUID


@dataclass(frozen=True)
class ResearchResultResponseDTO:
    id: UUID
    research_session_id: UUID
    opportunity_score: int
    demand_level: str
    competition_level: str
    profit_level: str
    summary: str
    created_at: datetime
    updated_at: datetime
