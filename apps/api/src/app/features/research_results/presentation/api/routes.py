from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.features.research_results.application.dtos import CreateResearchResultRequestDTO
from app.features.research_results.application.use_cases.create_research_result import (
    CreateResearchResultUseCase,
)
from app.features.research_results.presentation.api.dependencies import (
    get_create_research_result_use_case,
)
from app.features.research_sessions.domain.exceptions import ResearchSessionNotFoundError

router = APIRouter(
    prefix="/research-sessions/{research_session_id}/research-result",
    tags=["research-results"],
    dependencies=[Depends(verify_api_key)],
)


class ResearchResultResponse(BaseModel):
    id: UUID
    research_session_id: UUID
    opportunity_score: int
    demand_level: str
    competition_level: str
    profit_level: str
    summary: str
    created_at: datetime
    updated_at: datetime


@router.get("", response_model=ResearchResultResponse, status_code=200)
async def get_research_result(
    research_session_id: UUID,
    use_case: CreateResearchResultUseCase = Depends(  # noqa: B008
        get_create_research_result_use_case
    ),
) -> ResearchResultResponse:
    try:
        result = await use_case.execute(
            CreateResearchResultRequestDTO(research_session_id=research_session_id)
        )
    except ResearchSessionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return ResearchResultResponse(
        id=result.id,
        research_session_id=result.research_session_id,
        opportunity_score=result.opportunity_score,
        demand_level=result.demand_level,
        competition_level=result.competition_level,
        profit_level=result.profit_level,
        summary=result.summary,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
