from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps.project import ProjectRepoDep
from src.api.deps.user import UserRepoDep
from src.repos.project_member import ProjectMemberRepository
from src.services.project_member import ProjectMemberService


def get_member_repo(session: AsyncSession) -> ProjectMemberRepository:
    return ProjectMemberRepository(session)


MemberRepoDep = Annotated[ProjectMemberRepository, Depends(get_member_repo)]


def get_member_service(
    member_repo: ProjectMemberRepository,
    project_repo: ProjectRepoDep,
    user_repo: UserRepoDep
) -> ProjectMemberService:
    return ProjectMemberService(member_repo, project_repo, user_repo)


MemberServiceDep = Annotated[ProjectMemberService, Depends(get_member_service)]
