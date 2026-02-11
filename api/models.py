from datetime import datetime

from pydantic import BaseModel


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    priority: int = 3
    due_date: datetime | None = None


class TaskCreate(TaskBase):
    pass


class Task(TaskBase):
    id: int
    created_at: datetime
    is_completed: bool = False

    class Config:
        from_attributes = True
