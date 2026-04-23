from typing import Any
from uuid import UUID

from sqlalchemy import select, or_

from src.models.task import Task
from src.repos.base import BaseRepository
from src.models.membership import ProjectMember, MemberStatus


class TaskRepository(BaseRepository[Task]):
    """
    Task repository class
    """

    model = Task
    eq_filter_map = {
        'status': Task.status,
        'priority': Task.priority,
        'project_id': Task.project_id,
    }
    range_filter_map = {
        'due_date_from': (Task.due_date, '>='),
        'due_date_to': (Task.due_date, '<='),
    }

    async def get_all_by_owner(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[Task], int]:
        stmt = select(Task).where(Task.owner_id == user_id)
        return await self.get_paginated(stmt, offset, limit, filters)

    async def get_accessible_tasks(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
        filters: dict | None = None
    ) -> tuple[list[Task], int]:
        stmt = (
            select(Task)
            .outerjoin(ProjectMember, ProjectMember.project_id == Task.project_id)
            .where(
                or_(
                    Task.owner_id == user_id,
                    (ProjectMember.user_id == user_id) &
                    (ProjectMember.status == MemberStatus.ACCEPTED)
                )
            )
            .distinct()
        )
        return await self.get_paginated(stmt, offset, limit, filters)
