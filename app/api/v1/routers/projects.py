from typing import Annotated

from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException

from sqlalchemy import select

from app.api.dependencies import (
    SessionDep,
    CurrentUserDep
)

from app.models.project import Project as ProjectModel
from app.schemas.project import Project, ProjectCreate, ProjectUpdate


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


@router.post(
    path='/',
    response_model=Project,
    status_code=status.HTTP_201_CREATED
)
async def create_project(
    session: SessionDep,
    current_user: CurrentUserDep,
    project_data: ProjectCreate
) -> Project:
    project = ProjectModel(
        **project_data.model_dump(),
        owner=current_user
    )
    
    session.add(project)
    session.commit()
    session.refresh(project)

    return project


@router.get(
    path='/{project_id}',
    response_model=Project,
    status_code=status.HTTP_200_OK
)
async def read_project(
    session: SessionDep,
    current_user: CurrentUserDep,
    project_id: int
) -> Project:
    project = session.get(ProjectModel, project_id)

    if project is None or project.owner != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Project not found'
        )
    
    return project


@router.patch(
    path='/{project_id}',
    response_model=Project,
    status_code=status.HTTP_200_OK
)
async def update_project(
    session: SessionDep,
    current_user: CurrentUserDep,
    project_id: int,
    project_data: ProjectUpdate
) -> Project:
    project = session.get(ProjectModel, project_id)

    if project is None or project.owner != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Project not found'
        )
    
    update_data = project_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value)
    
    session.commit()
    session.refresh(project)

    return project


@router.delete(
    path='/{project_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_project(
    session: SessionDep,
    current_user: CurrentUserDep,
    project_id: int
) -> None:
    project = session.get(ProjectModel, project_id)

    if project is None or project.owner != current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Project not found'
        )
    
    session.delete(project)
    session.commit()

    return None
