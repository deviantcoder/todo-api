from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class UserCreate(BaseModel):
    username: str = Field(..., min_length=5, max_length=50)
    email: EmailStr = Field(..., max_length=200)
    full_name: str | None = Field(None, max_length=200)
    password: str = Field(..., min_length=6, max_length=32)


class UserUpdate(BaseModel):
    username: str | None = Field(None, min_length=5, max_length=50)
    email: EmailStr | None = Field(None, max_length=200)
    full_name: str | None = Field(None, max_length=200)


class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
