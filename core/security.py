from typing import Any
from datetime import datetime, timedelta

from passlib.context import CryptContext
from jose import jwt

from core.config import Settings


pwd_context = CryptContext(schemes=['bcrypt'])


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(
    data: dict[str, Any],
    expires_delta: timedelta | None = None
):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({'exp': expire})

    encoded_jwt = jwt.encode(
        claims=to_encode,
        key=Settings.SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt
