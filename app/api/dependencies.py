from typing import Annotated

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from jose import jwt, JWTError

from app.models.user import User
from app.models.task import Task

from app.core.database import SessionLocal
from app.core.config import settings
from app.core.security import ALGORITHM


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/v1/auth/token',
    scheme_name='JWT'
)


def get_session():
    with SessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_current_user(
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(
            token=token,
            key=settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise credentials_exception
    
    email = payload.get('sub')

    if email is None:
        raise credentials_exception
    
    db_user = session.scalars(
        select(User).where(User.email == email)
    ).first()

    if db_user is None:
        raise credentials_exception
    
    return db_user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


def get_user_task(
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: int
) -> Task:
    task = session.get(Task, task_id)

    if task is None or task.owner != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found'
        )
    
    return task


UserTaskDep = Annotated[Task, Depends(get_user_task)]
