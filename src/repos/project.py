from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select

from src.models.project import Project
from src.models.project_member import MemberStatus, ProjectMember
from src.models.task import Task, TaskStatus
from src.repos.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """
    Project repository class
    """

    model = Project
    eq_filter_map = {
        'status': Project.status,
    }
    range_filter_map = {
        'due_date_from': (Project.due_date, '>='),
        'due_date_to': (Project.due_date, '<='),
    }

    async def get_all_by_owner(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[Project], int]:
        stmt = select(Project).where(Project.owner_id == user_id)
        return await self.get_paginated(stmt, offset, limit, filters)

    async def get_accessible_projects(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[Project], int]:
        stmt = (
            select(Project)
            .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
            .where(
                or_(
                    Project.owner_id == user_id,
                    (ProjectMember.user_id == user_id) & (ProjectMember.status == MemberStatus.ACCEPTED)
                )
            )
            .distinct()
        )
        return await self.get_paginated(stmt, offset, limit, filters)

    async def get_task_counts(self, project_id: UUID) -> dict[str, int]:
        active = await self.session.scalar(
            select(func.count()).where(
                Task.project_id == project_id,
                Task.status == TaskStatus.ACTIVE
            )
        ) or 0
        completed = await self.session.scalar(
            select(func.count()).where(
                Task.project_id == project_id,
                Task.status == TaskStatus.COMPLETED
            )
        ) or 0

        return {'active': active, 'completed': completed}
