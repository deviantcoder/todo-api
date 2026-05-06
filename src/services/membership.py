from uuid import UUID

from src.core.exceptions import (
    AlreadyExistsException,
    ForbiddenException,
    InvalidOperationException,
    NotFoundException,
)
from src.infra.caching.cache_keys import get_cache_key
from src.infra.caching.cache_manager import CacheManager
from src.infra.caching.cache_service import CacheService
from src.infra.security.permissions import can_manage_members
from src.models.membership import MemberRole, MemberStatus, ProjectMember
from src.models.project import Project
from src.models.user import User
from src.repos.membership import ProjectMemberRepository
from src.repos.project import ProjectRepository
from src.repos.user import UserRepository
from src.schemas.membership import InviteMemberRequest


class ProjectMemberService:
    """
    Service layer for managing project memberships.

    Handles member invitations, role updates, access control, and member
    removal for projects. Uses caching to reduce redundant project lookups.

    Attributes:
        member_repo (MemberRepository): Repository for project membership data access.
        project_repo (ProjectRepository): Repository for project data access.
        user_repo (UserRepository): Repository for user data access.
        cache (CacheService): Low-level cache service for direct cache interactions.
    """

    def __init__(
        self,
        member_repo: ProjectMemberRepository,
        project_repo: ProjectRepository,
        user_repo: UserRepository,
        cache: CacheService,
    ) -> None:
        self.member_repo = member_repo
        self.project_repo = project_repo
        self.user_repo = user_repo
        self.project_cache = CacheManager[Project](cache, Project)

    async def _get_project(self, project_id: UUID) -> Project:
        """
        Retrieve a project by ID, using the cache where possible.
        """

        project = await self.project_cache.get_or_fetch(
            get_cache_key('project:id', project_id),
            lambda: self.project_repo.get_by_id(project_id),
            use_cache=True
        )

        return project

    async def _get_membership(self, project_id: UUID, user_id: UUID) -> ProjectMember:
        """
        Retrieve a specific project membership, raising an error if not found.
        """

        membership = await self.member_repo.get_membership(project_id, user_id)
        if membership is None:
            raise NotFoundException('Membership not found')
        return membership

    async def _require_manage_permission(self, project_id: UUID, user: User) -> None:
        """
        Ensure the given user has permission to manage members of a project.
        """

        project = await self._get_project(project_id)
        membership = await self.member_repo.get_membership(project.id, user.id)

        if membership is None or not can_manage_members(membership):
            raise ForbiddenException()

    async def get_members(self, project_id: UUID, current_user: User) -> list[ProjectMember]:
        """
        Retrieve all members of a project.
        """

        project = await self._get_project(project_id)
        membership = await self.member_repo.get_membership(project.id, current_user.id)

        if membership is None:
            raise ForbiddenException('Only project members can view member list')

        if membership.status == MemberStatus.PENDING:
            raise ForbiddenException()

        if membership.role == MemberRole.VIEWER:
            raise ForbiddenException('Viewers cannot view member list')

        return await self.member_repo.get_project_members(project_id)

    async def invite(self, project_id: UUID, data: InviteMemberRequest, current_user: User) -> ProjectMember:
        """
        Invite a user to a project.
        """

        await self._require_manage_permission(project_id, current_user)

        invitee = await self.user_repo.get_by_username(data.username)
        if invitee is None:
            raise NotFoundException(f'User {data.username} not found')

        existing = await self.member_repo.get_membership(project_id, invitee.id)
        if existing is not None:
            raise AlreadyExistsException('User is already a member or has pending invite')

        member = ProjectMember(
            project_id=project_id,
            user_id=invitee.id,
            role=data.role,
            status=MemberStatus.PENDING
        )

        return await self.member_repo.create(member)

    async def accept_invite(self, project_id: UUID, current_user: User) -> ProjectMember:
        """
        Accept a pending project invitation.
        """

        project = await self._get_project(project_id)
        membership = await self._get_membership(project.id, current_user.id)

        if membership.status == MemberStatus.ACCEPTED:
            raise InvalidOperationException('Invite already accepted')

        return await self.member_repo.update(membership, {'status': MemberStatus.ACCEPTED})

    async def update_role(self, project_id: UUID, user_id: UUID, role: MemberRole, current_user: User) -> ProjectMember:
        """
        Update the role of a project member.
        """

        await self._require_manage_permission(project_id, current_user)

        membership = await self._get_membership(project_id, user_id)
        if membership.role == MemberRole.OWNER:
            raise InvalidOperationException('Cannot change role for project owner')

        return await self.member_repo.update(membership, {'role': role})

    async def remove_member(self, project_id: UUID, user_id: UUID, current_user: User) -> None:
        """
        Remove a member from a project.
        """

        await self._require_manage_permission(project_id, current_user)

        membership = await self._get_membership(project_id, user_id)
        if membership.role == MemberRole.OWNER:
            raise InvalidOperationException('Cannot remove project owner')

        await self.member_repo.delete(membership)

    async def leave(self, project_id: UUID, current_user: User) -> None:
        """
        Remove the current user from a project.
        """

        membership = await self._get_membership(project_id, current_user.id)
        if membership.role == MemberRole.OWNER:
            raise InvalidOperationException('Owner cannot leave - transfer ownership or delete the project')

        await self.member_repo.delete(membership)
