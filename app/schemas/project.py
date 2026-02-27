from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class BaseProject(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=500)


class ProjectCreate(BaseProject):
    pass


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_digits=500)
    is_archived: bool | None = None


class Project(BaseProject):
    id: int
    owner_id: int
    is_archived: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ProjectWithStats(Project):
    task_count: int = 0
    open_task_count: int = 0
