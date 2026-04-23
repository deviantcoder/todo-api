from typing import Annotated

from fastapi import Depends

from src.api.deps.session import SessionDep
from src.repos.project import ProjectRepository
from src.repos.membership import ProjectMemberRepository
from src.repos.task import TaskRepository
from src.repos.user import UserRepository


def get_member_repo(session: SessionDep) -> ProjectMemberRepository:
    return ProjectMemberRepository(session)


def get_project_repo(session: SessionDep) -> ProjectRepository:
    return ProjectRepository(session)


def get_user_repo(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_task_repo(session: SessionDep) -> TaskRepository:
    return TaskRepository(session)


MemberRepoDep = Annotated[ProjectMemberRepository, Depends(get_member_repo)]
ProjectRepoDep = Annotated[ProjectRepository, Depends(get_project_repo)]
UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
TaskRepoDep = Annotated[TaskRepository, Depends(get_task_repo)]
