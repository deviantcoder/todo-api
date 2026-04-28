from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select

from src.models.project import Project
from src.models.membership import MemberStatus, ProjectMember
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

    # async def get_accessible_projects(
    #     self,
    #     user_id: UUID,
    #     offset: int,
    #     limit: int,
    #     filters: dict[str, Any] | None = None
    # ) -> tuple[list[Project], int]:
    #     stmt = (
    #         select(Project)
    #         .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
    #         .where(
    #             or_(
    #                 Project.owner_id == user_id,
    #                 (ProjectMember.user_id == user_id) & (ProjectMember.status == MemberStatus.ACCEPTED)
    #             )
    #         )
    #         .distinct()
    #     )
    #     return await self.get_paginated(stmt, offset, limit, filters)

    async def get_accessible_projects(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[dict], int]:
        active_count = (
            select(func.count())
            .where(Task.project_id == Project.id, Task.status == TaskStatus.ACTIVE)
            .correlate(Project)
            .scalar_subquery()
        )
        completed_count = (
            select(func.count())
            .where(Task.project_id == Project.id, Task.status == TaskStatus.COMPLETED)
            .correlate(Project)
            .scalar_subquery()
        )

        stmt = (
            select(
                Project,
                active_count.label('active_tasks'),
                completed_count.label('completed_tasks')
            )
            .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
            .where(
                or_(
                    Project.owner_id == user_id,
                    (ProjectMember.user_id == user_id) &
                    (ProjectMember.status == MemberStatus.ACCEPTED)
                )
            )
            .distinct()
        )

        if filters:
            stmt = self._apply_filters(stmt, filters)
        
        total = await self.session.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0

        result = await self.session.execute(stmt.offset(offset).limit(limit))
        rows = result.all()

        return [
            {
                'project': project,
                'active_tasks': active,
                'completed_tasks': completed
            }
            for project, active, completed in rows
        ], total

    async def get_task_counts(self, project_id: UUID) -> dict[str, int]:
        counts = select(
            func.count().filter(Task.status == TaskStatus.ACTIVE).label('active'),
            func.count().filter(Task.status == TaskStatus.COMPLETED).label('completed')
        ).where(Task.project_id == project_id)

        result = await self.session.execute(counts)
        active, completed = result.one()

        return {'active': active, 'completed': completed}
