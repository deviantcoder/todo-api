from uuid import UUID

from src.core.exceptions import ForbiddenException, NotFoundException
from src.models.project import Project
from src.models.project_member import MemberRole, MemberStatus, ProjectMember
from src.models.user import User
from src.repos.project import ProjectRepository
from src.repos.project_member import ProjectMemberRepository
from src.schemas.pagination import PagedResponse, PaginationParams
from src.schemas.project import (
    ProjectCreate,
    ProjectFilterParams,
    ProjectResponse,
    ProjectUpdate,
)
from src.services.base import BaseService


class ProjectService(BaseService[Project, ProjectResponse]):
    """
    Project service class
    """

    def __init__(
        self,
        project_repo: ProjectRepository,
        member_repo: ProjectMemberRepository
    ) -> None:
        self.project_repo = project_repo
        self.member_repo = member_repo

    async def _get_project_for_user(self, project_id: UUID, user: User) -> Project:
        project = await self.project_repo.get_by_id(project_id)

        if project is None:
            raise NotFoundException('Project not found')

        if project.owner_id != user.id:
            raise ForbiddenException()

        return project

    async def get_all(
        self,
        user: User,
        pg_params: PaginationParams,
        filters: ProjectFilterParams | None = None
    ) -> PagedResponse[ProjectResponse]:
        filters_dict = filters.model_dump(exclude_none=True) if filters else {}
        items, total = await self.project_repo.get_all_by_owner(
            user.id, pg_params.offset, pg_params.limit, filters_dict
        )
        return await self.paginate(items, total, pg_params)

    async def get_by_id(self, project_id: UUID, user: User) -> Project:
        return await self._get_project_for_user(project_id, user)

    async def create(self, data: ProjectCreate, user: User) -> Project:
        project = Project(**data.model_dump(exclude_unset=True), owner_id=user.id)
        await self.project_repo.create(project)

        owner_membership = ProjectMember(
            project_id=project.id,
            user_id=user.id,
            role=MemberRole.OWNER,
            status=MemberStatus.ACCEPTED
        )

        await self.member_repo.create(owner_membership)

        return project

    async def update(self, project_id: UUID, data: ProjectUpdate, user: User) -> Project:
        project = await self._get_project_for_user(project_id, user)
        return await self.project_repo.update(project, data.model_dump(exclude_unset=True))

    async def delete(self, project_id: UUID, user: User) -> None:
        project = await self._get_project_for_user(project_id, user)
        return await self.project_repo.delete(project)
