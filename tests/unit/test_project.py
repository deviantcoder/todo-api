from uuid import uuid4

import pytest

from src.core.exceptions import ForbiddenException, NotFoundException
from src.models.project import ProjectStatus
from src.schemas.pagination import PaginationParams
from src.schemas.project import ProjectCreate, ProjectFilterParams, ProjectUpdate
from src.services.project import ProjectService
from tests.factories import ProjectFactory, UserFactory


def get_user_and_project() -> tuple:
    user = UserFactory.build()
    project = ProjectFactory.build(owner_id=user.id)

    return user, project


class TestGetById:
    async def test_success(self, project_repo, project_service: ProjectService):
        user, project = get_user_and_project()

        project_repo.get_by_id.return_value = project

        result = await project_service.get_by_id(project.id, user)

        assert result.id == project.id

    async def test_raises_if_not_found(self, project_repo, project_service: ProjectService):
        user = UserFactory.build()

        project_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await project_service.get_by_id(uuid4(), user)

    async def test_raises_if_not_owner(self, project_repo, project_service: ProjectService):
        user = UserFactory.build()
        _, project = get_user_and_project()

        project_repo.get_by_id.return_value = project

        with pytest.raises(ForbiddenException):
            await project_service.get_by_id(project.id, user)


class TestGetAll:
    async def test_success(self, project_repo, project_service: ProjectService):
        user = UserFactory.build()
        projects = [ProjectFactory.build(owner_id=user.id) for _ in range(3)]
        pg_params = PaginationParams()  # type: ignore

        project_repo.get_accessible_projects.return_value = (projects, len(projects))

        result = await project_service.get_all(user, pg_params)

        assert result.total == len(projects)
        assert len(result.items) == len(projects)

    async def test_empty(self, project_repo, project_service: ProjectService):
        user = UserFactory.build()
        pg_params = PaginationParams()  # type: ignore

        project_repo.get_accessible_projects.return_value = ([], 0)

        result = await project_service.get_all(user, pg_params)

        assert result.total == 0
        assert result.items == []

    async def test_with_filters(self, project_repo, project_service: ProjectService):
        user = UserFactory.build()
        projects = [
            ProjectFactory.build(owner_id=user.id, status=ProjectStatus.ACTIVE),
        ]
        pg_params = PaginationParams()  # type: ignore
        filters = ProjectFilterParams(status=ProjectStatus.ACTIVE)

        project_repo.get_accessible_projects.return_value = (projects, len(projects))

        result = await project_service.get_all(user, pg_params, filters)

        assert result.total == 1


class TestCreate:
    async def test_success(self, project_repo, project_service: ProjectService):
        user, project = get_user_and_project()
        data = ProjectCreate(title='Test Project', owner_id=user.id)  # type: ignore

        project_repo.create.return_value = project

        result = await project_service.create(data, user)

        project_repo.create.assert_called_once()
        assert result.owner_id == user.id


class TestUpdate:
    async def test_success(self, project_repo, project_service: ProjectService):
        user, project = get_user_and_project()
        data = ProjectUpdate(title='Updated project title')  # type: ignore
        updated_project = ProjectFactory.build(title=data.title)

        project_repo.get_by_id.return_value = project
        project_repo.update.return_value = updated_project

        result = await project_service.update(project.id, data, user)

        project_repo.update.assert_called_once()
        assert result.title == data.title

    async def test_raises_if_not_found(self, project_repo, project_service: ProjectService):
        user, _ = get_user_and_project()
        data = ProjectUpdate(title='Updated project title')  # type: ignore

        project_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await project_service.update(uuid4(), data, user)

    async def test_raises_if_not_owner(self, project_repo, project_service: ProjectService):
        user, _ = get_user_and_project()
        other_user, project = get_user_and_project()
        data = ProjectUpdate(title='Updated project title')  # type: ignore

        project_repo.get_by_id.return_value = project

        with pytest.raises(ForbiddenException):
            await project_service.update(project.id, data, user)


class TestDelete:
    async def test_success(self, project_repo, project_service: ProjectService):
        user, project = get_user_and_project()

        project_repo.get_by_id.return_value = project

        await project_service.delete(project.id, user)
        project_repo.delete.assert_called_once()

    async def test_raises_if_not_found(self, project_repo, project_service: ProjectService):
        user, _ = get_user_and_project()

        project_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await project_service.delete(uuid4(), user)

    async def test_raises_if_not_owner(self, project_repo, project_service: ProjectService):
        user, _ = get_user_and_project()
        other_user, project = get_user_and_project()

        project_repo.get_by_id.return_value = project

        with pytest.raises(ForbiddenException):
            await project_service.delete(project.id, user)
