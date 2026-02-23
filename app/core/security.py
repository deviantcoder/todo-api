from typing import Any

from datetime import datetime, timezone, timedelta

from pwdlib import PasswordHash
from jose import jwt

from app.core.config import settings


pwd_hash = PasswordHash.recommended()

ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = 'HS256'


def get_password_hash(password: str) -> str:
    return pwd_hash.hash(password)


def verify_password(password: str, hash: str) -> bool:
    return pwd_hash.verify(password, hash)


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
) -> str:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({'exp': expire})

    access_token = jwt.encode(
        claims=to_encode,
        key=settings.SECRET_KEY,
        algorithm=ALGORITHM
    )

    return access_token
