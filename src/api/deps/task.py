from typing import Annotated

from fastapi import Depends

from src.api.deps.session import SessionDep
from src.repos.task import TaskRepository
from src.services.task import TaskService
from src.api.deps.project import ProjectRepoDep


def get_task_repo(session: SessionDep) -> TaskRepository:
    return TaskRepository(session)


TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repo)]


def get_task_service(task_repo: TaskRepoDep, project_repo: ProjectRepoDep) -> TaskService:
    return TaskService(task_repo, project_repo)


TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
