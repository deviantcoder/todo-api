from uuid import UUID

from src.core.exceptions import ForbiddenException, NotFoundException
from src.models.task import Task
from src.models.user import User
from src.repos.project import ProjectRepository
from src.repos.task import TaskRepository
from src.schemas.pagination import PagedResponse, PaginationParams
from src.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from src.services.base import BaseService


class TaskService(BaseService[Task, TaskResponse]):
    """
    Task service class
    """

    def __init__(self, task_repo: TaskRepository, project_repo: ProjectRepository) -> None:
        self.task_repo = task_repo
        self.project_repo = project_repo

    async def _get_task_for_user(self, task_id: UUID, user: User) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        if task is None:
            raise NotFoundException('Task not found')

        if task.owner != user:
            raise ForbiddenException()

        return task

    async def get_all(self, user: User, pg_params: PaginationParams) -> PagedResponse[TaskResponse]:
        items, total = await self.task_repo.get_all_by_owner(user.id, pg_params.offset, pg_params.limit)
        return await self.paginate(items, total, pg_params)

    async def get_by_id(self, task_id: UUID, user: User) -> Task:
        return await self._get_task_for_user(task_id, user)

    async def create(self, data: TaskCreate, user: User) -> Task:
        if data.project_id:
            project = await self.project_repo.get_by_id(data.project_id)
            if not project:
                raise NotFoundException('Project not found')
            if project.owner_id != user.id:
                raise ForbiddenException()

        task = Task(**data.model_dump(exclude_unset=True), owner_id=user.id)

        return await self.task_repo.create(task)

    async def update(self, task_id: UUID, data: TaskUpdate, user: User) -> Task:
        task = await self._get_task_for_user(task_id, user)
        return await self.task_repo.update(task, data.model_dump(exclude_unset=True))

    async def delete(self, task_id: UUID, user: User) -> None:
        task = await self._get_task_for_user(task_id, user)
        return await self.task_repo.delete(task)
