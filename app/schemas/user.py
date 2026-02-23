from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class BaseUser(BaseModel):
    email: EmailStr = Field(max_length=200)
    full_name: str | None = Field(default=None, max_length=200)


class UserCreate(BaseUser):
    password: str = Field(min_length=8)


class User(BaseUser):
    id: int
    is_active: bool
    created_at: datetime
