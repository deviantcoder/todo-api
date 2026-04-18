from uuid import UUID, uuid4

import pytest

from src.core.exceptions import (
    AlreadyExistsException,
    ForbiddenException,
    InvalidOperationException,
    NotFoundException,
)
from src.models.project_member import MemberRole, MemberStatus
from src.schemas.project_member import InviteMemberRequest
from src.services.project_member import ProjectMemberService
from tests.factories import ProjectFactory, ProjectMemberFactory, UserFactory


def make_membership(
    project_id: UUID,
    user_id: UUID,
    role: MemberRole = MemberRole.OWNER,
    status: MemberStatus = MemberStatus.ACCEPTED
):
    return ProjectMemberFactory(
        project_id=project_id,
        user_id=user_id,
        role=role,
        status=status
    )


def create_user_project_membership(
    role: MemberRole = MemberRole.OWNER,
    status: MemberStatus = MemberStatus.ACCEPTED
) -> tuple:
    user = UserFactory.build()
    project = ProjectFactory.build(owner=user)
    membership = make_membership(project.id, user.id, role, status)

    return (user, project, membership)


class TestGetMembers:
    async def test_owner_can_view_members(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        owner, project, owner_membership = create_user_project_membership()

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = owner_membership
        member_repo.get_project_members.return_value = [owner_membership]

        result = await member_service.get_members(project.id, owner)

        member_repo.get_project_members.assert_called_once()
        member_repo.get_project_members.assert_called_once_with(project.id)
        assert len(result) == 1
        assert result[0].user_id == owner.id
        assert result[0].project_id == project.id

    async def test_member_can_view_members(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        _, project, owner_membership = create_user_project_membership()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = membership
        member_repo.get_project_members.return_value = [owner_membership, membership]

        result = await member_service.get_members(project.id, member)

        assert len(result) == 2
        assert membership in result
        assert owner_membership in result

    async def test_viewer_cannot_view_members(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        project = ProjectFactory.build()
        viewer = UserFactory.build()
        viewer_membership = make_membership(project.id, viewer.id, MemberRole.VIEWER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = viewer_membership

        with pytest.raises(ForbiddenException):
            await member_service.get_members(project.id, viewer)


    async def test_non_member_cannot_view_members(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        project = ProjectFactory.build()
        non_member = UserFactory.build()

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = None

        with pytest.raises(ForbiddenException):
            await member_service.get_members(project.id, non_member)

    async def test_raises_if_project_not_found(
        self, project_repo, member_service: ProjectMemberService
    ):
        user = UserFactory.build()
        project_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await member_service.get_members(uuid4(), user)


class TestInvite:
    async def test_owner_can_invite(
        self, project_repo, member_repo, user_repo, member_service: ProjectMemberService
    ):
        owner, project, owner_membership = create_user_project_membership()
        other_user = UserFactory.build()
        other_user_membership = make_membership(
            project.id, other_user.id, MemberRole.MEMBER, MemberStatus.PENDING
        )

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.side_effect = [owner_membership, None]
        user_repo.get_by_username.return_value = other_user
        member_repo.create.return_value = other_user_membership

        data = InviteMemberRequest(username=other_user.username)

        result = await member_service.invite(project.id, data, owner)

        member_repo.create.assert_called_once()
        assert result.user_id == other_user.id
        assert result.project_id == project.id
        assert result.role == other_user_membership.role
        assert result.status == MemberStatus.PENDING

    async def test_non_owner_cannot_invite(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        project = ProjectFactory.build()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = membership

        data = InviteMemberRequest(username='some_user')

        with pytest.raises(ForbiddenException):
            await member_service.invite(project.id, data, member)

    async def test_raises_if_user_not_found(
        self, user_repo, project_repo, member_repo, member_service: ProjectMemberService
    ):
        owner, project, owner_membership = create_user_project_membership()

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = owner_membership
        user_repo.get_by_username.return_value = None

        data = InviteMemberRequest(username='some_user')

        with pytest.raises(NotFoundException):
            await member_service.invite(project.id, data, owner)

    async def test_raises_if_already_member(
        self, project_repo, member_repo, user_repo, member_service: ProjectMemberService
    ):
        owner, project, owner_membership = create_user_project_membership()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.side_effect = [owner_membership, membership]
        user_repo.get_by_username.return_value = member

        data = InviteMemberRequest(username=member.username)

        with pytest.raises(AlreadyExistsException):
            await member_service.invite(project.id, data, owner)


class TestAcceptInvite:
    async def test_success(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        user, project, membership = create_user_project_membership(
            MemberRole.MEMBER, MemberStatus.PENDING
        )
        updated_membership = make_membership(
            project.id, user.id, status=MemberStatus.ACCEPTED
        )

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = membership
        member_repo.update.return_value = updated_membership

        result = await member_service.accept_invite(project.id, user)

        member_repo.update.assert_called_once()
        assert result.status == MemberStatus.ACCEPTED

    async def test_raises_if_already_accepted(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        user, project, membership = create_user_project_membership(MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = membership

        with pytest.raises(InvalidOperationException):
            await member_service.accept_invite(project.id, user)

    async def test_raises_if_no_invite(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        project = ProjectFactory.build()
        user = UserFactory.build()

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = None

        with pytest.raises(NotFoundException):
            await member_service.accept_invite(project.id, user)


class TestUpdateRole:
    async def test_owner_can_update_role(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        owner, project, owner_membership = create_user_project_membership()
        member = UserFactory.build()
        member_membership = make_membership(project.id, member.id, MemberRole.MEMBER)
        updated_membership = make_membership(project.id, member.id, MemberRole.VIEWER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.side_effect = [owner_membership, member_membership]
        member_repo.update.return_value = updated_membership

        result = await member_service.update_role(
            project.id, member.id, MemberRole.VIEWER, owner
        )

        member_repo.update.assert_called_once()
        assert result.role == MemberRole.VIEWER

    async def test_non_owner_cannot_update_role(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        project = ProjectFactory.build()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = membership

        with pytest.raises(ForbiddenException):
            await member_service.update_role(
                project.id, uuid4(), MemberRole.VIEWER, member
            )

    async def test_raises_if_changing_owner_role(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
       owner, project, owner_membership = create_user_project_membership()

       project_repo.get_by_id.return_value = project
       member_repo.get_membership.return_value = owner_membership

       with pytest.raises(InvalidOperationException):
           await member_service.update_role(
               project.id, owner.id, MemberRole.MEMBER, owner
           )


class TestRemoveMember:
    async def test_owner_can_remove_member(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        owner, project, owner_membership = create_user_project_membership()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.side_effect = [owner_membership, membership]
        member_repo.delete.return_value = None

        result = await member_service.remove_member(project.id, member.id, owner)

        member_repo.delete.assert_called_once()
        assert result is None

    async def test_non_owner_cannot_remove_member(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        project = ProjectFactory.build()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = membership

        with pytest.raises(ForbiddenException):
            await member_service.remove_member(project.id, uuid4(), member)

    async def test_raises_if_removing_owner(
        self, project_repo, member_repo, member_service: ProjectMemberService
    ):
        owner, project, _ = create_user_project_membership()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        project_repo.get_by_id.return_value = project
        member_repo.get_membership.return_value = membership

        with pytest.raises(ForbiddenException):
            await member_service.remove_member(project.id, owner.id, member)


class TestLeave:
    async def test_member_can_leave(self, member_repo, member_service: ProjectMemberService):
        project = ProjectFactory.build()
        member = UserFactory.build()
        membership = make_membership(project.id, member.id, MemberRole.MEMBER)

        member_repo.get_membership.return_value = membership

        await member_service.leave(project.id, member)

        member_repo.delete.assert_called_once()
        member_repo.delete.assert_called_once_with(membership)

    async def test_owner_cannot_leave(self, member_repo, member_service: ProjectMemberService):
        owner, project, owner_membership = create_user_project_membership()

        member_repo.get_membership.return_value = owner_membership

        with pytest.raises(InvalidOperationException):
            await member_service.leave(project.id, owner)

    async def test_raises_if_not_member(self, member_repo, member_service: ProjectMemberService):
        user = UserFactory.build()
        member_repo.get_membership.return_value = None

        with pytest.raises(NotFoundException):
            await member_service.leave(uuid4(), user)
