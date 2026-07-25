from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.features.projects.domain.exceptions import ProjectNotFoundError
from app.features.research_sessions.application.dtos import (
    CreateResearchSessionRequestDTO,
    ListResearchSessionsRequestDTO,
    ResearchSessionDTO,
)
from app.features.research_sessions.application.use_cases.create_research_session import (
    CreateResearchSessionUseCase,
)
from app.features.research_sessions.application.use_cases.list_research_sessions import (
    ListResearchSessionsForProjectUseCase,
)
from app.features.research_sessions.domain.entities.research_session import (
    Marketplace,
    ResearchSessionStatus,
)
from app.features.research_sessions.presentation.api.dependencies import (
    get_create_research_session_use_case,
    get_list_research_sessions_use_case,
)

router = APIRouter(
    prefix="/projects/{project_id}/research-sessions",
    tags=["research-sessions"],
    dependencies=[Depends(verify_api_key)],
)


class CreateResearchSessionRequest(BaseModel):
    marketplace: Marketplace


class ResearchSessionResponse(BaseModel):
    id: UUID
    project_id: UUID
    marketplace: Marketplace
    status: ResearchSessionStatus
    created_at: datetime
    updated_at: datetime


def _to_response(dto: ResearchSessionDTO) -> ResearchSessionResponse:
    return ResearchSessionResponse(
        id=dto.id,
        project_id=dto.project_id,
        marketplace=dto.marketplace,
        status=dto.status,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post("", response_model=ResearchSessionResponse, status_code=201)
async def create_research_session(
    project_id: UUID,
    payload: CreateResearchSessionRequest,
    use_case: CreateResearchSessionUseCase = Depends(  # noqa: B008
        get_create_research_session_use_case
    ),
) -> ResearchSessionResponse:
    try:
        result = await use_case.execute(
            CreateResearchSessionRequestDTO(project_id=project_id, marketplace=payload.marketplace)
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return _to_response(result)


@router.get("", response_model=list[ResearchSessionResponse], status_code=200)
async def list_research_sessions(
    project_id: UUID,
    use_case: ListResearchSessionsForProjectUseCase = Depends(  # noqa: B008
        get_list_research_sessions_use_case
    ),
) -> list[ResearchSessionResponse]:
    try:
        results = await use_case.execute(ListResearchSessionsRequestDTO(project_id=project_id))
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return [_to_response(result) for result in results]
