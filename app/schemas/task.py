from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict


class BaseTask(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    due_date: datetime | None = None
    priority: int = Field(default=3, ge=1, le=5)


class Task(BaseTask):
    id: int
    is_completed: bool = False
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class TaskCreate(BaseTask):
    pass


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    due_date: datetime | None = None
    priority: int | None = None
    is_completed: bool | None = None
