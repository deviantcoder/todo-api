from uuid import UUID

from src.core.caching.cache_keys import get_cache_key
from src.core.caching.cache_manager import CacheManager
from src.core.caching.cache_service import CacheService
from src.core.exceptions import ForbiddenException
from src.core.security.permissions import can_edit_tasks, can_view_tasks
from src.models.membership import MemberRole
from src.models.project import Project
from src.models.task import Task
from src.models.user import User
from src.repos.membership import ProjectMemberRepository
from src.repos.project import ProjectRepository
from src.repos.task import TaskRepository
from src.schemas.pagination import PagedResponse, PaginationParams
from src.schemas.task import TaskCreate, TaskFilterParams, TaskResponse, TaskUpdate
from src.services.base import BaseService


class TaskService(BaseService[Task, TaskResponse]):
    """
    Task service class
    """

    CACHE_PREFIX: str = 'task:id'

    def __init__(
        self,
        task_repo: TaskRepository,
        project_repo: ProjectRepository,
        member_repo: ProjectMemberRepository,
        cache: CacheService,
    ) -> None:
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.member_repo = member_repo
        self.task_cache = CacheManager[Task](cache, Task)
        self.project_cache = CacheManager[Project](cache, Project)

    async def _get_task(self, task_id: UUID, use_cache: bool = True) -> Task:
        return await self.task_cache.get_or_fetch(
            key=get_cache_key(self.CACHE_PREFIX, task_id),
            fetch=lambda: self.task_repo.get_by_id(task_id),
            use_cache=use_cache
        )

    async def _get_project_access(self, project_id: UUID, user: User) -> MemberRole:
        project = await self.project_cache.get_or_fetch(
            get_cache_key('project:id', project_id),
            lambda: self.project_repo.get_by_id(project_id),
            use_cache=True
        )

        if project.owner_id == user.id:
            return MemberRole.OWNER

        membership = await self.member_repo.get_membership(project.id, user.id)

        if membership is None or not can_view_tasks(membership):
            raise ForbiddenException()

        if can_edit_tasks(membership):
            return MemberRole.MEMBER

        return MemberRole.VIEWER
    
    async def _check_view_permission(self, task: Task, user: User) -> None:
        if task.project_id is None:
            if task.owner_id != user.id:
                raise ForbiddenException()
            return
        
        await self._get_project_access(task.project_id, user)

    async def _check_edit_permission(self, task: Task, user: User) -> None:
        if task.owner_id == user.id:
            return
        
        if task.project_id:
            access = await self._get_project_access(task.project_id, user)
            if access == MemberRole.VIEWER:
                raise ForbiddenException()
            return
        
        raise ForbiddenException()

    async def get_all(
        self,
        user: User,
        pg_params: PaginationParams,
        filters: TaskFilterParams | None = None,
    ) -> PagedResponse[TaskResponse]:
        if filters is not None and filters.project_id is not None:
            await self._get_project_access(filters.project_id, user)

        filters_dict = filters.model_dump(exclude_none=True) if filters else {}

        items, total = await self.task_repo.get_accessible_tasks(
            user.id, pg_params.offset, pg_params.limit, filters_dict
        )
        return await self.paginate(items, total, pg_params)

    async def get_by_id(self, task_id: UUID, user: User) -> Task:
        task = await self._get_task(task_id, use_cache=True)
        await self._check_view_permission(task, user)
        return task

    async def create(self, data: TaskCreate, user: User) -> Task:
        if data.project_id:
            await self._get_project_access(data.project_id, user)

        task = Task(**data.model_dump(exclude_unset=True), owner_id=user.id)
        created = await self.task_repo.create(task)

        await self.task_cache.set(
            get_cache_key(self.CACHE_PREFIX, created.id),
            created
        )

        return created

    async def update(self, task_id: UUID, data: TaskUpdate, user: User) -> Task:
        task = await self._get_task(task_id, use_cache=False)
        await self._check_edit_permission(task, user)

        updated = await self.task_repo.update(task, data.model_dump(exclude_unset=True))
        await self.task_cache.set(
            get_cache_key(self.CACHE_PREFIX, task.id),
            updated
        )

        return updated

    async def delete(self, task_id: UUID, user: User) -> None:
        task = await self._get_task(task_id, use_cache=False)

        await self._check_edit_permission(task, user)
        await self.task_repo.delete(task)
        await self.task_cache.invalidate(get_cache_key(self.CACHE_PREFIX, task.id))
