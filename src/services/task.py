from uuid import UUID

from src.core.exceptions import ForbiddenException, NotFoundException
from src.core.security.permissions import can_edit_tasks, can_view_tasks
from src.models.task import Task
from src.models.user import User
from src.repos.project import ProjectRepository
from src.repos.membership import ProjectMemberRepository
from src.repos.task import TaskRepository
from src.schemas.pagination import PagedResponse, PaginationParams
from src.schemas.task import TaskCreate, TaskFilterParams, TaskResponse, TaskUpdate
from src.services.base import BaseService


class TaskService(BaseService[Task, TaskResponse]):
    """
    Task service class
    """

    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        member_repo: ProjectMemberRepository
    ) -> None:
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def _get_task_for_user(self, task_id: UUID, user: User) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        if task is None:
            raise NotFoundException('Task not found')

        if task.owner_id != user.id:
            raise ForbiddenException()

        return task

    async def _get_project_access(self, project_id: UUID, user: User) -> str:
        project = await self.project_repo.get_by_id(project_id)

        if project is None:
            raise NotFoundException('Project not found')

        if project.owner_id == user.id:
            return 'owner'

        membership = await self.member_repo.get_membership(project.id, user.id)

        if membership is None or not can_view_tasks(membership):
            raise ForbiddenException()

        if can_edit_tasks(membership):
            return 'member'

        return 'viewer'

    async def _get_task_and_check_view(self, task_id: UUID, user: User) -> Task:
        task = await self.task_repo.get_by_id(task_id)

        if task is None:
            raise NotFoundException('Task not found')

        if task.project_id is None:
            if task.owner_id != user.id:
                raise ForbiddenException()
            return task

        await self._get_project_access(task.project_id, user)
        return task

    async def _get_task_and_check_edit(self, task_id: UUID, user: User) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if task is None:
            raise NotFoundException('Task not found')

        if task.owner_id == user.id:
            return task

        access = await self._get_project_access(task.project_id, user)
        if access == 'viewer':
            raise ForbiddenException()

        return task

    async def get_all(
        self,
        user: User,
        pg_params: PaginationParams,
        filters: TaskFilterParams | None = None
    ) -> PagedResponse[TaskResponse]:
        if filters is not None and filters.project_id is not None:
            await self._get_project_access(filters.project_id, user)

        filters_dict = filters.model_dump(exclude_none=True) if filters else {}

        items, total = await self.task_repo.get_accessible_tasks(
            user.id, pg_params.offset, pg_params.limit, filters_dict
        )
        return await self.paginate(items, total, pg_params)

    async def get_by_id(self, task_id: UUID, user: User) -> Task:
        return await self._get_task_and_check_view(task_id, user)

    async def create(self, data: TaskCreate, user: User) -> Task:
        if data.project_id:
            await self._get_project_access(data.project_id, user)

        task = Task(**data.model_dump(exclude_unset=True), owner_id=user.id)

        return await self.task_repo.create(task)

    async def update(self, task_id: UUID, data: TaskUpdate, user: User) -> Task:
        task = await self._get_task_and_check_edit(task_id, user)
        return await self.task_repo.update(task, data.model_dump(exclude_unset=True))

    async def delete(self, task_id: UUID, user: User) -> None:
        task = await self._get_task_and_check_edit(task_id, user)
        return await self.task_repo.delete(task)
