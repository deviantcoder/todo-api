from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.models.project import ProjectStatus


class ProjectCreate(BaseModel):
    title: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=500)
    due_date: datetime | None = None


class ProjectUpdate(BaseModel):
    title: str | None = Field(None, max_length=200)
    description: str | None = Field(None, max_length=500)
    due_date: datetime | None = None
    status: ProjectStatus | None = None


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: str | None
    due_date: datetime | None
    status: ProjectStatus
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
