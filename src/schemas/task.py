from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=500)
    priority: TaskPriority = TaskPriority.LOW
    due_date: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = Field(None, max_length=500)
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None


class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    due_date: datetime | None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
