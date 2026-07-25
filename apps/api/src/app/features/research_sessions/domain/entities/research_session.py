from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID


class Marketplace(StrEnum):
    AMAZON = "amazon"
    EBAY = "ebay"
    TIKTOK = "tiktok"


class ResearchSessionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass(frozen=True)
class ResearchSession:
    id: UUID
    project_id: UUID
    marketplace: Marketplace
    status: ResearchSessionStatus
    created_at: datetime
    updated_at: datetime
