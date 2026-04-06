from uuid import uuid4

import pytest

from src.core.exceptions import ForbiddenException, NotFoundException
from src.schemas.pagination import PaginationParams
from src.schemas.task import TaskCreate, TaskFilterParams, TaskUpdate
from src.services.task import TaskService
from tests.factories import ProjectFactory, TaskFactory, UserFactory


def get_user_and_task():
    user = UserFactory.build()
    task = TaskFactory.build(owner_id=user.id)

    return user, task


class TestGetById:
    async def test_success(self, task_repo, task_service: TaskService):
        user, task = get_user_and_task()

        task_repo.get_by_id.return_value = task

        result = await task_service.get_by_id(task.id, user)

        assert result.id == task.id

    async def test_raises_if_not_found(self, task_repo, task_service: TaskService):
        user = UserFactory.build()

        task_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await task_service.get_by_id(uuid4(), user)

    async def test_raises_if_not_owner(self, task_repo, task_service: TaskService):
        _, task = get_user_and_task()
        other_user = UserFactory.build()

        task_repo.get_by_id.return_value = task

        with pytest.raises(ForbiddenException):
            await task_service.get_by_id(task.id, other_user)


class TestGetAll:
    async def test_success(self, task_repo, task_service: TaskService):
        user = UserFactory.build()
        tasks = [TaskFactory.build(owner_id=user.id) for _ in range(3)]
        pg_params = PaginationParams()  # type: ignore

        task_repo.get_all_by_owner.return_value = (tasks, 3)

        result = await task_service.get_all(user, pg_params)

        assert result.total == 3
        assert len(result.items) == 3

    async def test_raises_if_project_not_found(self, task_service: TaskService, project_repo):
        user = UserFactory.build()
        pg_params = PaginationParams()  # type: ignore
        filters = TaskFilterParams(project_id=uuid4())

        project_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await task_service.get_all(user, pg_params, filters)

    async def test_raises_if_project_not_owned(self, task_service: TaskService, project_repo):
        user = UserFactory.build()
        other_user = UserFactory.build()
        project = ProjectFactory.build(owner_id=other_user.id)
        pg_params = PaginationParams()  # type: ignore
        filters = TaskFilterParams(project_id=project.id)

        project_repo.get_by_id.return_value = project

        with pytest.raises(ForbiddenException):
            await task_service.get_all(user, pg_params, filters)

class TestCreate:
    async def test_success(self, task_repo, task_service: TaskService, project_repo):
        user = UserFactory.build()
        project = ProjectFactory.build(owner_id=user.id)
        task = TaskFactory.build(project_id=project.id, owner_id=user.id)
        data = TaskCreate(title='Test task', project_id=project.id)  # type: ignore

        project_repo.get_by_id.return_value = project
        task_repo.create.return_value = task

        result = await task_service.create(data, user)

        task_repo.create.assert_called_once()
        assert result.owner_id == user.id

    async def test_raises_if_project_not_found(self, task_service: TaskService, project_repo):
        user = UserFactory.build()
        data = TaskCreate(title='Test task', project_id=uuid4())  # type: ignore

        project_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await task_service.create(data, user)


    async def test_raises_if_project_not_owned(self, task_service: TaskService, project_repo):
        user = UserFactory.build()
        other_user = UserFactory.build()
        project = ProjectFactory.build(owner_id=other_user.id)
        data = TaskCreate(title='Test task', project_id=project.id)  # type: ignore

        project_repo.get_by_id.return_value = project

        with pytest.raises(ForbiddenException):
            await task_service.create(data, user)


class TestUpdate:
    async def test_success(self, task_repo, task_service: TaskService):
        user, task = get_user_and_task()
        updated_task = TaskFactory.build(owner_id=user.id, title='New task title')
        data = TaskUpdate(title='New task title')  # type: ignore

        task_repo.get_by_id.return_value = task
        task_repo.update.return_value = updated_task

        result = await task_service.update(task.id, data, user)

        task_repo.update.assert_called_once()
        assert result.title == data.title

    async def test_raises_if_not_found(self, task_repo, task_service: TaskService):
        user = UserFactory.build()
        data = TaskUpdate(title='New task title')  # type: ignore

        task_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await task_service.update(uuid4(), data, user)

    async def test_raises_if_not_owner(self, task_repo, task_service: TaskService):
        user = UserFactory.build()
        _, task = get_user_and_task()
        data = TaskUpdate(title='New task title')  # type: ignore

        task_repo.get_by_id.return_value = task

        with pytest.raises(ForbiddenException):
            await task_service.update(task.id, data, user)


class TestDelete:
    async def test_success(self, task_repo, task_service: TaskService):
        user, task = get_user_and_task()

        task_repo.get_by_id.return_value = task

        await task_service.delete(task.id, user)

        task_repo.delete.assert_called_once()

    async def test_raises_if_not_found(self, task_repo, task_service: TaskService):
        user = UserFactory.build()

        task_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            await task_service.delete(uuid4(), user)

    async def test_raises_if_not_owner(self, task_repo, task_service: TaskService):
        user = UserFactory.build()
        _, task = get_user_and_task()

        task_repo.get_by_id.return_value = task

        with pytest.raises(ForbiddenException):
            await task_service.delete(task.id, user)
