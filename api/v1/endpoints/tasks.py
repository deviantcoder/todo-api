from typing import Annotated
from datetime import datetime

from fastapi import APIRouter, Query, Depends, status
from fastapi.exceptions import HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from schemas.task import Task, TaskCreate, TaskUpdate
from api.dependencies import SessionDep
from models.task import Task as TaskModel


router = APIRouter(prefix='/tasks', tags=['tasks'])


@router.get(
    path='/',
    response_model=list[Task],
    status_code=status.HTTP_200_OK,
    tags=['tasks']    
)
async def list_tasks(
    db: SessionDep,
    completed: Annotated[
        bool | None, Query(description='Filter by completion status')
    ] = None,
    priority_le: Annotated[
        int | None, Query(description='Show only tasks with priority ≤ this value')
    ] = None,
    skip: Annotated[
        int, Query(ge=0, description='Pagination - items to skip')
    ] = 0,
    limit: Annotated[
        int, Query(ge=1, le=100, description='Pagination - max items to return')
    ] = 10
):
    stmt = select(TaskModel)

    if completed is not None:
        stmt = stmt.where(TaskModel.is_completed == completed)

    if priority_le is not None:
        stmt = stmt.where(TaskModel.priority <= priority_le)

    stmt = stmt.offset(skip).limit(limit).order_by(TaskModel.created_at.desc())

    tasks = db.scalars(stmt).all()

    return tasks


@router.get(
    path='/{task_id}',
    response_model=Task,
    status_code=status.HTTP_200_OK,
    tags=['tasks']
)
async def get_task(
    db: SessionDep,
    task_id: int
):
    task = db.get(TaskModel, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Task not found'
        )
    
    return task


@router.post(
    path='/',
    response_model=Task,
    status_code=status.HTTP_201_CREATED,    
    tags=['tasks']
)
async def create_task(
    db: SessionDep,
    task: TaskCreate
):
    db_task = TaskModel(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@router.patch(
    path='/{task_id}',
    response_model=Task,
    status_code=status.HTTP_200_OK,
    tags=['tasks']
)
async def update_task(
    db: SessionDep,
    task_id: int,
    task_in: TaskUpdate
):
    task = db.get(TaskModel, task_id)

    update_data = task_in.model_dump(exclude_unset=True)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Task with id {task_id} not found'
        )
    
    for key, value in update_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)

    return task


@router.delete(
    path='/tasks/{task_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    db: SessionDep,
    task_id: int
):
    task = db.get(TaskModel, task_id)

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Task with id {task_id} not found'
        )
    
    db.delete(task)
    db.commit()

    return None
