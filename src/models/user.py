from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class User(Base):
    """
    User model class
    """

    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    refresh_tokens = relationship('RefreshToken', back_populates='owner')
    tasks = relationship('Task', back_populates='owner')
    projects = relationship('Project', back_populates='owner')
    project_memberships = relationship('ProjectMember', back_populates='user')

    def to_dict(self) -> dict:
        return {
            column.name: str(getattr(self, column.name))
            for column in self.__table__.columns
        }
