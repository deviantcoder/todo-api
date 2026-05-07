from typing import Annotated

from fastapi import Depends

from src.api.deps.cache import CacheServiceDep
from src.api.deps.db.repos import UserRepoDep
from src.services.user import UserService


def get_user_service(repo: UserRepoDep, cache: CacheServiceDep) -> UserService:
    return UserService(repo, cache)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
