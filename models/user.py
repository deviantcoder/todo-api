from datetime import datetime

from sqlalchemy import String, Integer, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(length=200), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(length=200), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(length=200), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

    tasks = relationship('Task', back_populates='owner')
