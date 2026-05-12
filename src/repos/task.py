from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select

from src.models.membership import MemberStatus, ProjectMember
from src.models.task import Task
from src.repos.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """
    Repository for managing tasks.
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
        """
        Retrieve a paginated list of tasks owned by a specific user.

        Args:
            user_id: ID (UUID) of the task owner.
            offset: The number of records to skip.
            limit: The maximum number of records to return.
            filters: Optional dictionary of filters to apply.
        """

        stmt = select(Task).where(Task.owner_id == user_id)
        return await self.get_paginated(stmt, offset, limit, filters)

    async def get_accessible_tasks(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
        filters: dict | None = None
    ) -> tuple[list[Task], int]:
        """
        Retrieve a paginated list of tasks accessible to a specific user.

        A task is considered accessible if the user is either the owner or an
        accepted member of the project the task belongs to.

        Args:
            user_id: ID (UUID) of the user.
            offset: The number of records to skip.
            limit: The maximum number of records to return.
            filters: Optional dictionary of filters to apply.
        """

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

    async def search(self, query: str, user_id: UUID, limit: int = 10) -> list[Task]:
        """
        Search for accessible tasks using a full-text search query.

        Args:
            query: The search query string.
            user_id: ID (UUID) of the user.
            limit: The maximum number of results to return.
        """

        tsquery = func.websearch_to_tsquery('english', query)

        inner = (
            select(Task.id)
            .outerjoin(ProjectMember, ProjectMember.project_id == Task.project_id)
            .where(
                Task.search_vector.op('@@')(tsquery),
                or_(
                    Task.owner_id == user_id,
                    (ProjectMember.user_id == user_id) &
                    (ProjectMember.status == MemberStatus.ACCEPTED)
                )
            )
            .distinct()
            .subquery()
        )

        stmt = (
            select(Task)
            .join(inner, Task.id == inner.c.id)
            .order_by(func.ts_rank(Task.search_vector, tsquery).desc())
            .limit(limit)
        )

        return list(await self.session.scalars(stmt))
