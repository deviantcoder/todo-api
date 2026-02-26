from datetime import datetime, timezone

from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    title: Mapped[str] = mapped_column(String(length=200), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(length=500), nullable=True)
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False, index=True)
    owner = relationship('User', back_populates='projects')

    tasks = relationship('Task', back_populates='project')
