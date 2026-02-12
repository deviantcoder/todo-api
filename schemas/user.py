from datetime import datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict
)


class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str = Field(min_length=8)


class UserOut(UserBase):
    id: int
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )


class UserInDB(UserOut):
    hashed_password: str
