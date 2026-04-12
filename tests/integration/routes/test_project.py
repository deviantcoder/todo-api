from typing import Any
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.project import Project, ProjectStatus
from src.models.user import User
from tests.factories import ProjectFactory, UserFactory


class TestGetProjects:
    URL: str = '/v1/projects/'

    async def test_success(self, project: Project, client: AsyncClient, auth_headers):
        response = await client.get(
            self.URL, headers=auth_headers
        )

        data = response.json()

        assert response.status_code == 200
        assert data['total'] >= 1
        assert len(data['items']) >= 1

    async def test_requires_auth(self, client: AsyncClient):
        response = await client.get(self.URL)
        assert response.status_code == 401

    async def test_filter_by_status(self, project: Project, client: AsyncClient, auth_headers):
        response = await client.get(
            self.URL, params={'status': project.status.value}, headers=auth_headers
        )

        data = response.json()

        assert response.status_code == 200
        assert all(t['status'] == project.status.value for t in data['items'])


class TestGetProject:
    URL: str = '/v1/projects/{}'

    async def test_success(self, project: Project, client: AsyncClient, auth_headers):
        response = await client.get(
            self.URL.format(str(project.id)), headers=auth_headers
        )

        assert response.status_code == 200
        assert response.json()['id'] == str(project.id)

    async def test_not_found(self, client: AsyncClient, auth_headers):
        response = await client.get(
            self.URL.format(str(uuid4())), headers=auth_headers
        )
        assert response.status_code == 404

    async def test_not_owned(self, user: User, db_session: AsyncSession, client: AsyncClient, auth_headers):
        other_user = UserFactory.build()
        project = ProjectFactory.build(owner_id=other_user.id)

        db_session.add(other_user)
        db_session.add(project)
        await db_session.commit()

        response = await client.get(
            self.URL.format(str(project.id)), headers=auth_headers
        )

        assert response.status_code == 403


class TestCreateProject:
    URL: str = '/v1/projects/'

    def _get_project_data(self, **kwargs) -> dict[str, Any]:
        return {
            'title': kwargs.get('title', 'Test task'),
            'description': kwargs.get('description', 'Test task description'),
        }

    async def test_create(self, user: User, client: AsyncClient, auth_headers):
        project_data = self._get_project_data()

        response = await client.post(
            self.URL, json=project_data, headers=auth_headers
        )
        data = response.json()

        assert response.status_code == 201
        for field, value in project_data.items():
            assert data[field] == value

    async def test_requires_auth(self, client: AsyncClient):
        response = await client.post(self.URL, json=self._get_project_data())
        assert response.status_code == 401


class TestUpdateProject:
    URL: str = '/v1/projects/{}'

    def _get_update_project_data(self, **kwargs) -> dict[str, Any]:
        return {
            'title': kwargs.get('title', 'Updated project title'),
            'description': kwargs.get('description', 'Updated project description'),
            'status': kwargs.get('status', ProjectStatus.ACTIVE.value),
            'due_date': kwargs.get('description', '2026-12-12T00:00:00'),
        }

    async def test_success(self, project: Project, client: AsyncClient, auth_headers):
        project_data = self._get_update_project_data()

        response = await client.patch(
            self.URL.format(str(project.id)), json=project_data, headers=auth_headers
        )

        data = response.json()

        assert response.status_code == 200

        for field, value in project_data.items():
            assert data[field] == value

    async def test_not_found(self, client: AsyncClient, auth_headers):
        project_data = self._get_update_project_data()

        response = await client.patch(
            self.URL.format(str(uuid4())), json=project_data, headers=auth_headers
        )

        assert response.status_code == 404

    async def test_not_owned(self, db_session: AsyncSession, client: AsyncClient, auth_headers):
        other_user = UserFactory.build()
        project = ProjectFactory.build(owner_id=other_user.id)
        project_data = self._get_update_project_data()

        db_session.add(other_user)
        db_session.add(project)
        await db_session.commit()

        response = await client.patch(
            self.URL.format(str(project.id)), json=project_data, headers=auth_headers
        )

        assert response.status_code == 403


class TestDeleteProjects:
    URL: str = '/v1/projects/{}'

    async def test_success(self, project: Project, client: AsyncClient, auth_headers):
        response = await client.delete(
            self.URL.format(str(project.id)), headers=auth_headers
        )

        assert response.status_code == 204

    async def test_not_found(self, client: AsyncClient, auth_headers):
        response = await client.delete(
            self.URL.format(str(uuid4())), headers=auth_headers
        )

        assert response.status_code == 404

    async def test_not_owned(self, db_session: AsyncSession, client: AsyncClient, auth_headers):
        other_user = UserFactory.build()
        project = ProjectFactory.build(owner_id=other_user.id)

        db_session.add(other_user)
        db_session.add(project)
        await db_session.commit()

        response = await client.delete(
            self.URL.format(str(project.id)), headers=auth_headers
        )

        assert response.status_code == 403
