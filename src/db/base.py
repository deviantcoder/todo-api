import uuid
from datetime import datetime
from typing import Any, Self

from sqlalchemy import UUID, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """
    Base model class with common attributes
    """

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )

    def to_dict(self) -> dict[str, Any]:
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, uuid.UUID):
                value = str(value)
            elif isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict) -> Self:
        for c in cls.__table__.columns:
            if isinstance(c.type, uuid.UUID) and isinstance(data.get(c.name), str):
                data[c.name] = uuid.UUID(data[c.name])
            elif isinstance(c.type, datetime) and isinstance(data.get(c.name), str):
                data[c.name] = datetime.fromisoformat(data[c.name])
        return cls(**data)
