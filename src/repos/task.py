from typing import Any
from uuid import UUID

from sqlalchemy import select

from src.models.task import Task
from src.repos.base import BaseRepository


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
