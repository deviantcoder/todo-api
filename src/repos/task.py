from uuid import UUID

from sqlalchemy import select, func

from .base import BaseRepository
from src.models.task import Task


class TaskRepository(BaseRepository[Task]):
    """
    Task repository class
    """

    model = Task

    async def get_all_by_owner(self, user_id: UUID, offset: int, limit: int) -> tuple[list[Task], int]:
        stmt = select(Task).where(Task.owner_id == user_id)

        total = await self.session.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0

        result = await self.session.scalars(stmt.offset(offset).limit(limit))

        return list(result.all()), total
