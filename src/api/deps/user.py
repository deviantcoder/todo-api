from typing import Annotated

from fastapi import Depends

from src.api.deps.session import SessionDep
from src.repos.user import UserRepository
from src.services.user import UserService


def get_user_repo(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]


def get_user_service(repo: UserRepoDep) -> UserService:
    return UserService(repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
