from datetime import datetime
from enum import StrEnum
from typing import Self
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

    @classmethod
    def from_row(cls, row: dict) -> Self:
        project = row['project']
        return cls(
            **{c.name: getattr(project, c.name) for c in project.__table__.columns},
            task_counts=TaskCounts(
                active=row['active_tasks'],
                completed=row['completed_tasks']
            )
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
