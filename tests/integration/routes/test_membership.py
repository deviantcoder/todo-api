from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project
from src.models.membership import MemberRole, MemberStatus, ProjectMember
from src.models.user import User


class TestGetMembers:
    URL: str = '/v1/projects/{}/members/'

    async def test_owner_can_get_members(
        self,
        project: Project,
        membership: ProjectMember,
        client: AsyncClient,
        auth_headers
    ):
        response = await client.get(
            self.URL.format(str(project.id)), headers=auth_headers
        )

        data = response.json()

        assert response.status_code == 200
        assert len(data) == 1
        assert any(str(membership.id) == item['id'] for item in data)

    async def test_member_can_get_members(
        self,
        project: Project,
        membership: ProjectMember,
        second_membership: ProjectMember,
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.get(
            self.URL.format(str(project.id)), headers=second_auth_headers
        )

        data = response.json()

        assert response.status_code == 200
        assert len(data) == 2
        assert any(str(membership.id) == item['id'] for item in data)
        assert any(str(second_membership.id) == item['id'] for item in data)

    async def test_viewer_cannot_get_members(
        self,
        db_session: AsyncSession,
        second_user: User,
        project: Project,
        client: AsyncClient,
        second_auth_headers
    ):
        viewer = ProjectMember(
            project_id=project.id,
            user_id=second_user.id,
            role=MemberRole.VIEWER,
            status=MemberStatus.ACCEPTED
        )

        db_session.add(viewer)
        await db_session.commit()

        response = await client.get(
            self.URL.format(str(project.id)), headers=second_auth_headers
        )

        assert response.status_code == 403

    async def test_requires_auth(
        self, client: AsyncClient, project: Project
    ):
        response = await client.get(self.URL.format(str(project.id)))
        assert response.status_code == 401

    async def test_project_not_found(self, client: AsyncClient, auth_headers):
        response = await client.get(
            self.URL.format(str(uuid4())), headers=auth_headers
        )
        assert response.status_code == 404

    async def test_membership_not_found(
        self, project: Project, client: AsyncClient, auth_headers
    ):
        response = await client.get(
            self.URL.format(str(project.id)), headers=auth_headers
        )
        assert response.status_code == 403


class TestInviteMember:
    URL: str = '/v1/projects/{}/members/invite'

    def _get_invite_data(self, **kwargs) -> dict[str, str]:
        return {
            'username': kwargs.get('username', 'some_username'),
            'role': kwargs.get('role', MemberRole.MEMBER.value),
        }

    async def test_owner_can_invite(
        self,
        project: Project,
        second_user: User,
        membership: ProjectMember,  # noqa
        client: AsyncClient,
        auth_headers
    ):
        data = self._get_invite_data(username=second_user.username)

        response = await client.post(
            self.URL.format(str(project.id)), json=data, headers=auth_headers
        )

        assert response.status_code == 201

    async def test_member_cannot_invite(
        self,
        project: Project,
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        second_auth_headers
    ):
        data = self._get_invite_data()

        response = await client.post(
            self.URL.format(str(project.id)), json=data, headers=second_auth_headers
        )

        assert response.status_code == 403

    async def test_invite_creates_pending_status(
        self,
        project: Project,
        second_user: User,
        membership: ProjectMember,  # noqa
        client: AsyncClient,
        auth_headers
    ):
        data = self._get_invite_data(username=second_user.username)

        response = await client.post(
            self.URL.format(str(project.id)), json=data, headers=auth_headers
        )

        assert response.status_code == 201
        assert response.json()['status'] == MemberStatus.PENDING.value

    async def test_cannot_invite_twice(
        self,
        project: Project,
        second_user: User,
        membership: ProjectMember,  # noqa
        client: AsyncClient,
        auth_headers
    ):
        data = self._get_invite_data(username=second_user.username)

        await client.post(
            self.URL.format(str(project.id)), json=data, headers=auth_headers
        )
        response = await client.post(
            self.URL.format(str(project.id)), json=data, headers=auth_headers
        )

        assert response.status_code == 400

    async def test_invite_unknown_user(
        self,
        project: Project,
        membership: ProjectMember,  # noqa
        client: AsyncClient,
        auth_headers
    ):
        data = self._get_invite_data()

        response = await client.post(
            self.URL.format(str(project.id)), json=data, headers=auth_headers
        )

        assert response.status_code == 404

    async def test_requires_auth(self, project: Project, client: AsyncClient):
        response = await client.post(self.URL.format(str(project.id)), json={})
        assert response.status_code == 401


class TestAcceptInvite:
    URL: str = '/v1/projects/{}/members/accept-invite'

    async def test_success(
        self,
        project: Project,
        second_pending_membership: ProjectMember,  # noqa
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.post(
            self.URL.format(str(project.id)), headers=second_auth_headers
        )

        assert response.status_code == 200
        assert response.json()['status'] == MemberStatus.ACCEPTED.value

    async def test_raises_if_already_accepted(
        self,
        project: Project,
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.post(
            self.URL.format(str(project.id)), headers=second_auth_headers
        )

        assert response.status_code == 400

    async def test_raises_if_no_invite(
        self,
        project: Project,
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.post(
            self.URL.format(str(project.id)), headers=second_auth_headers
        )

        assert response.status_code == 404

    async def test_requires_auth(
        self,
        project: Project,
        client: AsyncClient
    ):
        response = await client.post(self.URL.format(str(project.id)))
        assert response.status_code == 401


class TestUpdateMemberRole:
    URL: str = '/v1/projects/{}/members/{}/update-role'

    async def test_owner_can_update_role(
        self,
        project: Project,
        second_user: User,
        membership: ProjectMember,  # noqa
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        auth_headers
    ):
        response = await client.patch(
            self.URL.format(str(project.id), str(second_user.id)),
            json={'role': MemberRole.VIEWER},
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()['role'] == MemberRole.VIEWER.value

    async def test_member_cannot_update_role(
        self,
        project: Project,
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.patch(
            self.URL.format(str(project.id), str(uuid4())),
            json={'role': MemberRole.MEMBER.value},
            headers=second_auth_headers
        )

        assert response.status_code == 403

    async def test_raises_if_changing_for_owner(
        self,
        project: Project,
        second_user: User,
        membership: ProjectMember,  # noqa
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        db_session: AsyncSession,
        auth_headers
    ):
        second_membership.role = MemberRole.OWNER
        await db_session.commit()

        response = await client.patch(
            self.URL.format(str(project.id), str(second_user.id)),
            json={'role': MemberRole.VIEWER},
            headers=auth_headers
        )

        assert response.status_code == 400

    async def test_membership_not_found(
        self,
        project: Project,
        membership: ProjectMember,  # noqa
        second_user: User,
        client: AsyncClient,
        auth_headers
    ):
        response = await client.patch(
            self.URL.format(str(project.id), str(second_user.id)),
            json={'role': MemberRole.MEMBER},
            headers=auth_headers
        )

        assert response.status_code == 404

    async def test_requires_auth(self, client: AsyncClient):
        response = await client.patch(
            self.URL.format(str(uuid4()), str(uuid4())),
            json={'role': MemberRole.MEMBER}
        )

        assert response.status_code == 401


class TestRemoveMember:
    URL: str = '/v1/projects/{}/members/{}'

    async def test_owner_can_remove_member(
        self,
        project: Project,
        membership: ProjectMember,  # noqa
        second_membership: ProjectMember,  # noqa
        second_user: User,
        client: AsyncClient,
        auth_headers
    ):
        response = await client.delete(
            self.URL.format(str(project.id), str(second_user.id)), headers=auth_headers
        )

        assert response.status_code == 204

    async def test_non_owner_cannot_remove_member(
        self,
        project: Project,
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.delete(
            self.URL.format(str(project.id), str(uuid4())), headers=second_auth_headers
        )

        assert response.status_code == 403

    async def test_cannot_remove_owner(
        self,
        project: Project,
        user: User,
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.delete(
            self.URL.format(str(project.id), str(user.id)), headers=second_auth_headers
        )

        assert response.status_code == 403

    async def test_membership_not_found(
        self,
        project: Project,
        membership: ProjectMember,  # noqa
        client: AsyncClient,
        auth_headers
    ):
        response = await client.delete(
            self.URL.format(str(project.id), str(uuid4())), headers=auth_headers
        )

        assert response.status_code == 404


class TestLeaveProject:
    URL: str = '/v1/projects/{}/members/leave'

    async def test_member_can_leave(
        self,
        project: Project,
        second_membership: ProjectMember,  # noqa
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.delete(
            self.URL.format(str(project.id)), headers=second_auth_headers
        )

        assert response.status_code == 204


    async def test_owner_cannot_leave(
        self,
        project: Project,
        membership: ProjectMember,  # noqa
        client: AsyncClient,
        auth_headers
    ):
        response = await client.delete(
            self.URL.format(str(project.id)), headers=auth_headers
        )

        assert response.status_code == 400

    async def test_raises_if_not_member(
        self,
        project: Project,
        client: AsyncClient,
        second_auth_headers
    ):
        response = await client.delete(
            self.URL.format(str(project.id)), headers=second_auth_headers
        )

        assert response.status_code == 404

    async def test_requires_auth(
        self,
        project: Project,
        client: AsyncClient
    ):
        response = await client.delete(
            self.URL.format(str(project.id))
        )

        assert response.status_code == 401
