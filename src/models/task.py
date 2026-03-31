from uuid import UUID
from enum import StrEnum
from datetime import datetime

from sqlalchemy import String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class TaskStatus(StrEnum):
    ACTIVE = 'active'
    COMPLETED = 'completed'


class TaskPriority(StrEnum):
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


class Task(Base):
    """
    Task model class
    """

    __tablename__ = 'tasks'

    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text(500), nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.ACTIVE, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.LOW, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    owner = relationship('User', back_populates='tasks')

    project_id: Mapped[UUID] = mapped_column(ForeignKey('projects.id', ondelete='SET NULL'), nullable=True)
    project = relationship('Project', back_populates='tasks')
