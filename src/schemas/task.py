from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.task import TaskPriority, TaskStatus
from src.schemas.pagination import SortOrder


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=500)
    priority: TaskPriority = TaskPriority.LOW
    due_date: datetime | None = None
    project_id: UUID | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = Field(None, max_length=500)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    project_id: UUID | None = None


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    owner_id: UUID
    project_id: UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TaskSortField(StrEnum):
    CREATED_AT = 'created_at'
    DUE_DATE = 'due_date'
    STATUS = 'status'
    PRIORITY = 'priority'


class TaskFilterParams(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    project_id: UUID | None = None
    due_date_from: datetime | None = None
    due_date_to: datetime | None = None
    sort_by: TaskSortField = TaskSortField.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
