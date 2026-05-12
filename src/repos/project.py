from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select

from src.models.membership import MemberStatus, ProjectMember
from src.models.project import Project
from src.models.task import Task, TaskStatus
from src.repos.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """
    Repository for managing projects.
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
        """
        Retrieve a paginated list of projects owned by a specific user.

        Args:
            user_id: ID (UUID) of the project owner.
            offset: The number of records to skip.
            limit: The maximum number of records to return.
            filters: Optional dictionary of filter parameters to apply.
        """

        stmt = select(Project).where(Project.owner_id == user_id)
        return await self.get_paginated(stmt, offset, limit, filters)

    async def get_accessible_projects(
        self,
        user_id: UUID,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[dict], int]:
        """
        Retrieve a paginated list of projects accessible to a user.

        A project is considered accessible if the user is either the owner or an accepted member.

        Args:
            user_id: ID (UUID) of the user whose accessible projects are being fetched.
            offset: The number of records to skip.
            limit: The maximum number of records to return.
            filters: Optional dictionary of filters to apply.
        """

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
        """
        Retrieve the count of active and completed tasks for a given project.

        Args:
            project_id: ID (UUID) of the project to count tasks for.
        """

        counts = select(
            func.count().filter(Task.status == TaskStatus.ACTIVE).label('active'),
            func.count().filter(Task.status == TaskStatus.COMPLETED).label('completed')
        ).where(Task.project_id == project_id)

        result = await self.session.execute(counts)
        active, completed = result.one()

        return {'active': active, 'completed': completed}

    async def search(self, query: str, user_id: UUID, limit: int = 10) -> list[Project]:
        """
        Search for accessible projects using a full-text search query.

        Only projects owned by or shared with the user (as an accepted member) are returned.

        Args:
            query: The search query string.
            user_id: ID (UUID) of the user performing the search.
            limit: The maximum number of results to return.
        """

        tsquery = func.websearch_to_tsquery('english', query)

        inner = (
            select(Project.id)
            .outerjoin(ProjectMember, ProjectMember.project_id == Project.id)
            .where(
                Project.search_vector.op('@@')(tsquery),
                or_(
                    Project.owner_id == user_id,
                    (ProjectMember.user_id == user_id) &
                    (ProjectMember.status == MemberStatus.ACCEPTED)
                )
            )
            .distinct()
            .subquery()
        )

        stmt = (
            select(Project)
            .join(inner, Project.id == inner.c.id)
            .order_by(func.ts_rank(Project.search_vector, tsquery).desc())
            .limit(limit)
        )

        return list(await self.session.scalars(stmt))
