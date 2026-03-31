from uuid import UUID

from src.core.exceptions import (
    ForbiddenException,
    NotFoundException
)
from src.models.task import Task
from src.models.user import User
from src.repos.task import TaskRepository
from src.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """
    Task service class
    """

    def __init__(self, repo: TaskRepository) -> None:
        self.repo = repo

    async def _get_task_for_user(self, task_id: UUID, user: User) -> Task:
        task = await self.repo.get_by_id(task_id)

        if task is None:
            raise NotFoundException('Task not found')

        if task.owner != user:
            raise ForbiddenException()

        return task

    async def get_all(self, user: User) -> list[Task]:
        return await self.repo.get_all_by_owner(user.id)

    async def get_by_id(self, task_id: UUID, user: User) -> Task:
        return await self._get_task_for_user(task_id, user)

    async def create(self, data: TaskCreate, user: User) -> Task:
        task = Task(**data.model_dump(exclude_unset=True), owner_id=user.id)
        return await self.repo.create(task)

    async def update(self, task_id: UUID, data: TaskUpdate, user: User) -> Task:
        task = await self._get_task_for_user(task_id, user)
        return await self.repo.update(task, data.model_dump(exclude_unset=True))

    async def delete(self, task_id: UUID, user: User) -> None:
        task = await self._get_task_for_user(task_id, user)
        return await self.repo.delete(task)
