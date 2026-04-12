from uuid import UUID

from fastapi import APIRouter, status

from src.api.deps.auth import CurrentUserDep
from src.api.deps.pagination import PaginationDep
from src.api.deps.project import ProjectServiceDep, ProjectFiltersDep
from src.models.project import Project
from src.schemas.pagination import PagedResponse
from src.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate

router = APIRouter(prefix='/projects', tags=['projects'])


@router.get('/', response_model=PagedResponse[ProjectResponse])
async def get_projects(
    service: ProjectServiceDep,
    current_user: CurrentUserDep,
    pg_params: PaginationDep,
    filters: ProjectFiltersDep
) -> PagedResponse[ProjectResponse]:
    return await service.get_all(current_user, pg_params, filters)


@router.get('/{project_id}', response_model=ProjectResponse)
async def get_project(
    service: ProjectServiceDep,
    project_id: UUID,
    current_user: CurrentUserDep
) -> Project:
    return await service.get_by_id(project_id, current_user)


@router.post('/', response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    service: ProjectServiceDep,
    data: ProjectCreate,
    current_user: CurrentUserDep
) -> Project:
    return await service.create(data, current_user)


@router.patch('/{project_id}', response_model=ProjectResponse)
async def update_project(
    service: ProjectServiceDep,
    project_id: UUID,
    data: ProjectUpdate,
    current_user: CurrentUserDep
) -> Project:
    return await service.update(project_id, data, current_user)


@router.delete('/{project_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    service: ProjectServiceDep,
    project_id: UUID,
    current_user: CurrentUserDep
) -> None:
    return await service.delete(project_id, current_user)
