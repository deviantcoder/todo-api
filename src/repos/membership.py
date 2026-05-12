from uuid import UUID

from sqlalchemy import select

from src.models.membership import ProjectMember

from .base import BaseRepository


class ProjectMemberRepository(BaseRepository[ProjectMember]):
    """
    Repository for managing project membership data access operations.
    """

    model = ProjectMember

    async def get_membership(self, project_id: UUID, user_id: UUID) -> ProjectMember | None:
        """
        Retrieve a specific project membership record for a given project and user.

        Args:
            project_id: ID (UUID) of the project.
            user_id: ID (UUID) of the user.
        """

        return await self.session.scalar(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == user_id
            )
        )

    async def get_project_members(self, project_id: UUID) -> list[ProjectMember]:
        """Retrieve all members of a specific project.

        Args:
            project_id: ID (UUID) of the project.
        """

        result = await self.session.scalars(
            select(ProjectMember).where(ProjectMember.project_id == project_id)
        )
        return list(result.all())
