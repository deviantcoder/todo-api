from typing import Annotated

from fastapi import Depends

from src.api.deps.session import SessionDep
from src.repos.project import ProjectRepository
from src.schemas.project import ProjectFilterParams
from src.services.project import ProjectService


def get_project_repo(session: SessionDep) -> ProjectRepository:
    return ProjectRepository(session)


ProjectRepoDep = Annotated[ProjectRepository, Depends(get_project_repo)]


def get_project_service(repo: ProjectRepoDep) -> ProjectService:
    return ProjectService(repo)


ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]

ProjectFiltersDep = Annotated[ProjectFilterParams, Depends()]
