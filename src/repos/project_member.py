from .base import BaseRepository
from src.models.project_member import ProjectMember
from uuid import UUID
from sqlalchemy import select


class ProjectMemberRepository(BaseRepository[ProjectMember]):
    """
    Project member repository class
    """

    model = ProjectMember

    async def get_membership(self, project_id: UUID, user_id: UUID) -> ProjectMember | None:
        return await self.session.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        )

    async def get_project_members(self, project_id: UUID) -> list[ProjectMember]:
        result = await self.session.scalars(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )
        return list(result.all())
