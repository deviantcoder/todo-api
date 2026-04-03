from typing import Any
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute


class BaseRepository[T]:
    """
    Base repository class with common methods
    """

    model: type[T]

    eq_filter_map: dict[str, InstrumentedAttribute] = {}
    range_filter_map: dict[str, tuple[InstrumentedAttribute, str]] = {}

    def __init__(self, session: AsyncSession) -> None:
        if not hasattr(self, 'model'):
            raise NotImplementedError('Subclasses must define "model"')
        self.session = session

    def _apply_filters(self, stmt: Select,  filters: dict[str, Any]) -> Select:
        for field, column in self.eq_filter_map.items():
            if field in filters:
                stmt = stmt.where(column == filters[field])

        for field, (column, operator) in self.range_filter_map.items():
            if field in filters:
                if operator == '>=':
                    stmt = stmt.where(column >= filters[field])
                elif operator == '<=':
                    stmt = stmt.where(column <= filters[field])

        sort_by = filters.get('sort_by', 'created_at')
        sort_order = filters.get('sort_order', 'desc')

        sort_column = getattr(self.model, sort_by)
        order_func = asc if sort_order == 'asc' else desc

        return stmt.order_by(order_func(sort_column))

    async def get_all(self) -> list[T]:
        return list(await self.session.scalars(select(self.model)))

    async def get_paginated(
        self,
        stmt: Select,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[T], int]:
        if filters:
            stmt = self._apply_filters(stmt, filters)

        total = await self.session.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0
        result = await self.session.scalars(stmt.offset(offset).limit(limit))

        return list(result.all()), total

    async def get_by_id(self, id: UUID) -> T | None:
        return await self.session.get(self.model, id)

    async def create(self, instance: T) -> T:
        self.session.add(instance)

        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def update(self, instance: T, data: dict) -> T:
        for field, value in data.items():
            setattr(instance, field, value)

        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def delete(self, instance: T) -> None:
        await self.session.delete(instance)
        await self.session.commit()
