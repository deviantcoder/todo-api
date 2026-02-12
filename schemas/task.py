from datetime import datetime

from pydantic import (
    BaseModel,
    Field,
    ConfigDict
)


class TaskBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)
    priority: int = Field(default=3, ge=1, le=5)
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    created_at: datetime
    is_completed: bool = False

    model_config = ConfigDict(
        from_attributes=True
    )
