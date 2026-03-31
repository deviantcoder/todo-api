from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class ProjectStatus(StrEnum):
    ACTIVE = 'active'
    COMPLETED = 'completed'


class Project(Base):
    """
    Project model class
    """

    __tablename__ = 'projects'

    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text(500), nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)
    due_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    owner_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    owner = relationship('User', back_populates='projects')
    tasks = relationship('Task', back_populates='project')
