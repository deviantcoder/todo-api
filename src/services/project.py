from uuid import UUID

from src.core.caching.cache_manager import CacheManager
from src.core.caching.cache_service import CacheService
from src.core.exceptions import ForbiddenException
from src.models.membership import MemberRole, MemberStatus, ProjectMember
from src.models.project import Project
from src.models.user import User
from src.repos.membership import ProjectMemberRepository
from src.repos.project import ProjectRepository
from src.schemas.pagination import PagedResponse, PaginationParams
from src.schemas.project import (
    ProjectCreate,
    ProjectFilterParams,
    ProjectResponse,
    ProjectUpdate,
    TaskCounts,
)
from src.services.base import BaseService
from src.core.caching.cache_keys import get_cache_key


class ProjectService(BaseService[Project, ProjectResponse]):
    """
    Project service class
    """

    CACHE_PREFIX: str = 'project:id'

    def __init__(
        self,
        project_repo: ProjectRepository,
        member_repo: ProjectMemberRepository,
        cache: CacheService
    ) -> None:
        self.project_repo = project_repo
        self.member_repo = member_repo
        self.project_cache = CacheManager[Project](cache, Project)
    
    async def _get_project(self, project_id: UUID, use_cache: bool = True) -> Project:
        return await self.project_cache.get_or_fetch(
            self._project_key(project_id),
            lambda: self.project_repo.get_by_id(project_id),
            use_cache=use_cache
        )

    async def _get_project_for_user(self, project_id: UUID, user: User, require_owner: bool = False) -> Project:
        project = await self._get_project(project_id, use_cache=True)

        if project.owner_id == user.id:
            return project

        if require_owner:
            raise ForbiddenException()

        membership = await self.member_repo.get_membership(project.id, user.id)

        if membership is None or membership.status != MemberStatus.ACCEPTED:
            raise ForbiddenException()

        return project

    async def _attach_counts(self, project: Project) -> ProjectResponse:
        counts = await self.project_repo.get_task_counts(project.id)
        response = ProjectResponse.model_validate(project)
        response.task_counts = TaskCounts(**counts)
        return response
    
    def _project_key(self, project_id: UUID) -> str:
        return get_cache_key(self.CACHE_PREFIX, project_id)

    async def get_all(
        self,
        user: User,
        pg_params: PaginationParams,
        filters: ProjectFilterParams | None = None
    ) -> PagedResponse[ProjectResponse]:
        filters_dict = filters.model_dump(exclude_none=True) if filters else {}
        rows, total = await self.project_repo.get_accessible_projects(
            user.id, pg_params.offset, pg_params.limit, filters_dict
        )
        items = [ProjectResponse.from_row(row) for row in rows]
        return PagedResponse.create(items, total, pg_params)

    async def get_by_id(self, project_id: UUID, user: User) -> Project:
        return await self._get_project_for_user(project_id, user)

    async def create(self, data: ProjectCreate, user: User) -> Project:
        project = Project(**data.model_dump(exclude_unset=True), owner_id=user.id)
        created = await self.project_repo.create(project)

        await self.project_cache.set(self._project_key(created.id), created)

        owner_membership = ProjectMember(
            project_id=created.id,
            user_id=user.id,
            role=MemberRole.OWNER,
            status=MemberStatus.ACCEPTED
        )

        await self.member_repo.create(owner_membership)

        return project

    async def update(self, project_id: UUID, data: ProjectUpdate, user: User) -> Project:
        project = await self._get_project_for_user(project_id, user, require_owner=True)
        updated = await self.project_repo.update(project, data.model_dump(exclude_unset=True))

        await self.project_cache.set(self._project_key(project.id), updated)
        
        return updated

    async def delete(self, project_id: UUID, user: User) -> None:
        project = await self._get_project_for_user(project_id, user, require_owner=True)
        await self.project_repo.delete(project)
        await self.project_cache.invalidate(self._project_key(project.id))

