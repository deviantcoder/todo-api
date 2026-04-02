from uuid import UUID

from fastapi import APIRouter, status

from src.api.deps.task import TaskServiceDep
from src.api.deps.auth import CurrentUserDep
from src.models.task import Task
from src.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from src.schemas.pagination import PagedResponse
from src.api.deps.pagination import PaginationDep


router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get('/', response_model=PagedResponse[TaskResponse])
async def get_tasks(
    service: TaskServiceDep,
    current_user: CurrentUserDep,
    pg_params: PaginationDep
) -> PagedResponse[TaskResponse]:
    return await service.get_all(current_user, pg_params)


@router.get('/{task_id}', response_model=TaskResponse)
async def get_task(
    service: TaskServiceDep,
    task_id: UUID,
    current_user: CurrentUserDep
) -> Task:
    return await service.get_by_id(task_id, current_user)


@router.post('/', response_model=TaskResponse)
async def create_task(
    service: TaskServiceDep,
    data: TaskCreate,
    current_user: CurrentUserDep
) -> Task:
    return await service.create(data, current_user)


@router.patch('/{task_id}', response_model=TaskResponse)
async def update_task(
    service: TaskServiceDep,
    task_id: UUID,
    data: TaskUpdate,
    current_user: CurrentUserDep
):
    return await service.update(task_id, data, current_user)


@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    service: TaskServiceDep,
    task_id: UUID,
    current_user: CurrentUserDep
) -> None:
    return await service.delete(task_id, current_user)
