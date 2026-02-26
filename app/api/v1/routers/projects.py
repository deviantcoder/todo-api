from typing import Annotated

from fastapi import APIRouter, status

from sqlalchemy import select

from app.api.dependencies import (
    SessionDep,
    CurrentUserDep
)

from app.models.project import Project as ProjectModel
from app.schemas.project import Project


router = APIRouter(prefix='/projects', tags=['projects'])


@router.get(
    path='/',
    response_model=list[Project],
    status_code=status.HTTP_200_OK
)
async def list_projects(
    session: SessionDep,
    current_user: CurrentUserDep,
    archived: bool = False
) -> list[Project]:
    stmt = select(ProjectModel).where(ProjectModel.owner == current_user)

    if archived:
        stmt = stmt.where(ProjectModel.is_archived == True)

    projects = session.scalars(
        stmt.order_by(ProjectModel.created_at.desc())
    ).all()

    return projects
