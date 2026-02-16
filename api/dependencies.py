from typing import Annotated

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from jose import jwt, JWTError

from core.database import SessionLocal
from core.config import settings
from core.security import ALGORITHM

from models.user import User


def get_db():
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/v1/auth/login',
    scheme_name='JWT'
)


def get_current_user(
    db: SessionDep,
    token: str = Depends(oauth2_scheme)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(
            token=token, key=settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        email = payload.get('sub')
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.scalars(select(User).where(User.email == email)).first()

    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Inactive user'
        )
    
    return user
