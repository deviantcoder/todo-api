from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )


class ChangeUsernameRequest(BaseModel):
    password: str
    new_username: str = Field(..., min_length=5, max_length=50)


class ChangeEmailRequest(BaseModel):
    new_email: EmailStr = Field(..., max_length=200)


class ConfirmEmailChangeRequest(BaseModel):
    token: str
