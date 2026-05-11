from typing import Any
from uuid import UUID

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute


class BaseRepository[T]:
    """
    A generic base repository providing common database operations for SQLAlchemy models.

    This class is intended to be subclassed by concrete repositories that define
    a specific `model` class attribute. It provides methods for filtering, pagination,
    and standard CRUD operations using an async SQLAlchemy session.

    Attributes:
        model (type[T]): The SQLAlchemy model class this repository manages. Must be defined by subclasses.
        eq_filter_map (dict[str, InstrumentedAttribute]): A mapping of filter field names to model columns
            for equality filtering.
        range_filter_map (dict[str, tuple[InstrumentedAttribute, str]]): A mapping of filter field names to
            a tuple of (model column, operator) for range filtering. Supported operators are '>=' and '<='.
    """

    model: type[T]

    eq_filter_map: dict[str, InstrumentedAttribute] = {}
    range_filter_map: dict[str, tuple[InstrumentedAttribute, str]] = {}

    def __init__(self, session: AsyncSession) -> None:
        """
        Initialise the repository with an async database session.

        Args:
            session (AsyncSession): The SQLAlchemy async session.
        """

        if not hasattr(self, 'model'):
            raise NotImplementedError('Subclasses must define "model"')
        self.session = session

    def _apply_filters(self, stmt: Select,  filters: dict[str, Any]) -> Select:
        """
        Apply equality filters, range filters, and ordering to a SELECT statement.

        Iterates over `eq_filter_map` and `range_filter_map` to conditionally apply WHERE clauses based on
        the provided filters dict; applies ORDER BY using `sort_by` and `sort_order` filter keys.

        Args:
            stmt (Select): The base SQLAlchemy SELECT statement.
            filters (dict[str, Any]): A dictionary of filter parameters. Recognised keys include those defined
                in `eq_filter_map` and `range_filter_map`, as well as `sort_by` (default: 'created_at') and `sort_order`
        """

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
        """
        Retrieve all records for the model from the database.
        """

        return list(await self.session.scalars(select(self.model)))

    async def get_paginated(
        self,
        stmt: Select,
        offset: int,
        limit: int,
        filters: dict[str, Any] | None = None
    ) -> tuple[list[T], int]:
        """
        Retrieve a paginated list of records, optionally filtered and sorted.

        Applies filters if provided, queries the total count of matching records,
        and returns a page of results based on the given offset and limit.

        Args:
            stmt (Select): The base SQLAlchemy SELECT statement to paginate.
            offset (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            filters (dict[str, Any] | None): Optional filter parameters to apply using `_apply_filters`.
        """

        if filters:
            stmt = self._apply_filters(stmt, filters)

        total = await self.session.scalar(
            select(func.count()).select_from(stmt.subquery())
        ) or 0
        result = await self.session.scalars(stmt.offset(offset).limit(limit))

        return list(result.all()), total

    async def get_by_id(self, id: UUID) -> T | None:
        """
        Retrieve a single record by its primary key (UUID).

        Args:
            id (UUID): The primary key of the record to retrieve.
        """

        return await self.session.get(self.model, id)

    async def create(self, instance: T) -> T:
        """
        Save a new model instance to the database.

        Args:
            instance (T): The model instance to create.
        """

        self.session.add(instance)

        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def update(self, instance: T, data: dict) -> T:
        """
        Update an existing model instance with the provided data.

        Args:
            instance (T): The model instance to update.
            data (dict): A dictionary of field names and their new values.
        """

        instance = await self.session.merge(instance)

        for field, value in data.items():
            setattr(instance, field, value)

        await self.session.commit()
        await self.session.refresh(instance)

        return instance

    async def delete(self, instance: T) -> None:
        """
        Delete a model instance from the database.

        Args:
            instance (T): The model instance to delete.
        """

        await self.session.delete(instance)
        await self.session.commit()
