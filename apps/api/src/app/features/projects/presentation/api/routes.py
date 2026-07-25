from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import verify_api_key
from app.features.projects.application.dtos import (
    CreateProjectRequestDTO,
    GetProjectRequestDTO,
    ProjectDTO,
)
from app.features.projects.application.use_cases.create_project import CreateProjectUseCase
from app.features.projects.application.use_cases.get_project import GetProjectUseCase
from app.features.projects.application.use_cases.list_projects import ListProjectsUseCase
from app.features.projects.domain.exceptions import InvalidProjectNameError, ProjectNotFoundError
from app.features.projects.presentation.api.dependencies import (
    get_create_project_use_case,
    get_get_project_use_case,
    get_list_projects_use_case,
)

router = APIRouter(prefix="/projects", tags=["projects"], dependencies=[Depends(verify_api_key)])


class CreateProjectRequest(BaseModel):
    name: str


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime


def _to_response(dto: ProjectDTO) -> ProjectResponse:
    return ProjectResponse(
        id=dto.id,
        name=dto.name,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(
    payload: CreateProjectRequest,
    use_case: CreateProjectUseCase = Depends(get_create_project_use_case),  # noqa: B008
) -> ProjectResponse:
    try:
        result = await use_case.execute(CreateProjectRequestDTO(name=payload.name))
    except InvalidProjectNameError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _to_response(result)


@router.get("", response_model=list[ProjectResponse], status_code=200)
async def list_projects(
    use_case: ListProjectsUseCase = Depends(get_list_projects_use_case),  # noqa: B008
) -> list[ProjectResponse]:
    results = await use_case.execute()
    return [_to_response(result) for result in results]


@router.get("/{project_id}", response_model=ProjectResponse, status_code=200)
async def get_project(
    project_id: UUID,
    use_case: GetProjectUseCase = Depends(get_get_project_use_case),  # noqa: B008
) -> ProjectResponse:
    try:
        result = await use_case.execute(GetProjectRequestDTO(project_id=project_id))
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return _to_response(result)
