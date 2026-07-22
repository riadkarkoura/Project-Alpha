from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.features.projects.application.dtos import CreateProjectRequestDTO
from app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from app.features.projects.domain.exceptions import InvalidProjectNameError
from app.features.projects.presentation.api.dependencies import get_create_project_use_case

router = APIRouter(prefix="/projects", tags=["projects"])


class CreateProjectRequest(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    payload: CreateProjectRequest,
    use_case: CreateProjectUseCase = Depends(get_create_project_use_case),  # noqa: B008
) -> ProjectResponse:
    try:
        result = await use_case.execute(CreateProjectRequestDTO(name=payload.name))
    except InvalidProjectNameError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return ProjectResponse(
        id=result.id,
        name=result.name,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )
