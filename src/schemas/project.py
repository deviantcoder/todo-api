from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from src.models.project import ProjectStatus
from src.schemas.pagination import SortOrder


class ProjectCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=500)
    due_date: datetime | None = None


class ProjectUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = Field(None, max_length=500)
    due_date: datetime | None = None
    status: ProjectStatus | None = None


class TaskCounts(BaseModel):
    active: int
    completed: int


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    due_date: datetime | None
    status: ProjectStatus
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    task_counts: TaskCounts | None = None

    model_config = ConfigDict(
        from_attributes=True
    )


class ProjectSortField(StrEnum):
    CREATED_AT = 'created_at'
    DUE_DATE = 'due_date'
    STATUS = 'status'


class ProjectFilterParams(BaseModel):
    status: ProjectStatus | None = None
    due_date_from: datetime | None = None
    due_date_to: datetime | None = None
    sort_by: ProjectSortField = ProjectSortField.CREATED_AT
    sort_order: SortOrder = SortOrder.DESC
