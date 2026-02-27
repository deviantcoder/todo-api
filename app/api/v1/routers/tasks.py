from typing import Annotated

from fastapi import APIRouter, Query, status
from fastapi.exceptions import HTTPException

from sqlalchemy import select

from app.api.dependencies import (
    SessionDep,
    CurrentUserDep,
    UserTaskDep
)
from app.models.task import Task as TaskModel
from app.models.project import Project
from app.schemas.task import Task, TaskCreate, TaskUpdate


router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get(
    path='/',
    response_model=list[Task],
    status_code=status.HTTP_200_OK
)
async def list_tasks(
    session: SessionDep,
    current_user: CurrentUserDep,
    completed: bool | None = None,
    priority_le: Annotated[int | None, Query(ge=1, le=5)] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(le=100)] = 10,
    project_id: Annotated[int | None, Query(description='Filter tasks by project')] = None
) -> list[Task]:
    stmt = select(TaskModel).where(TaskModel.owner == current_user)

    if completed is not None:
        stmt = stmt.where(TaskModel.is_completed == completed)
    
    if priority_le is not None:
        stmt = stmt.where(TaskModel.priority <= priority_le)

    if project_id is not None:
        project = session.get(Project, project_id)
        
        if project is None or project.owner != current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid or unauthorized project'
            )
        
        stmt = stmt.where(TaskModel.project == project)
    
    stmt = stmt.offset(skip).limit(limit).order_by(TaskModel.created_at.desc())
    tasks = session.scalars(stmt).all()

    return tasks


@router.post(
    path='/',
    response_model=Task,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    session: SessionDep,
    current_user: CurrentUserDep,
    task_data: TaskCreate
) -> Task:
    if task_data.project_id:
        project = session.get(Project, task_data.project_id)
        if project is None or project.owner != current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid or unauthorized project'
            )

    task = TaskModel(
        **task_data.model_dump(),
        owner=current_user
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.get(
    path='/{task_id}',
    response_model=Task,
    status_code=status.HTTP_200_OK
)
async def read_task(task: UserTaskDep) -> Task:
    return task


@router.patch(
    path='/{task_id}',
    response_model=Task,
    status_code=status.HTTP_200_OK
)
async def update_task(
    session: SessionDep,
    task: UserTaskDep,
    task_data: TaskUpdate
) -> Task:
    update_data = task_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    session.commit()
    session.refresh(task)

    return task


@router.delete(
    path='/{task_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(session: SessionDep, task: UserTaskDep) -> None:    
    session.delete(task)
    session.commit()

    return None
