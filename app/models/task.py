from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(length=200), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(length=500), nullable=True)
    due_date: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    owner = relationship('User', back_populates='tasks')
