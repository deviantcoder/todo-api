from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class MemberRole(StrEnum):
    OWNER = 'owner'
    MEMBER = 'member'
    VIEWER = 'viewer'


class MemberStatus(StrEnum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'


class ProjectMember(Base):
    """
    Project member model class
    """

    __tablename__ = 'project_members'
    __table_args__ = (
        UniqueConstraint('project_id', 'user_id', name='uq_project_member'),
    )

    project_id: Mapped[UUID] = mapped_column(ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    role: Mapped[MemberRole] = mapped_column(Enum(MemberRole), default=MemberRole.MEMBER, nullable=False)
    status: Mapped[MemberStatus] = mapped_column(Enum(MemberStatus), default=MemberStatus.PENDING, nullable=False)

    project = relationship('Project', back_populates='members')
    user = relationship('User', back_populates='project_memberships')
