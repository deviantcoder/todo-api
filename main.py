from typing import Annotated

from datetime import datetime

from fastapi import FastAPI, Query, status
from fastapi.exceptions import HTTPException

from models import Task, TaskCreate


app = FastAPI(
    title='Todo API',
    description='A modern task & project management API',
    version='0.1.0'
)


fake_tasks_db = [
    Task(
        id=1,
        title='FastAPI',
        description='FastAPI path params',
        priority=1,
        due_date=datetime(2026, 2, 15),
        created_at=datetime.now(),
        is_completed=False
    ),
    Task(
        id=2,
        title='Django',
        description=None,
        priority=4,
        due_date=None,
        created_at=datetime.now(),
        is_completed=True
    ),
]


@app.get('/', tags=['root'])
async def read_root():
    return {'message': 'Welcome to Todo API'}


@app.get('/tasks/', response_model=list[Task], tags=['tasks'])
async def get_tasks(
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
        int, Query(le=100, description='Pagination - max items to return')
    ] = 10
):
    result = fake_tasks_db[:]

    if completed:
        result = [task for task in result if task.is_completed == completed]

    if priority_le:
        result = [task for task in result if task.priority <= priority_le]
    
    result = result[skip : skip + limit]

    return result


@app.get('/tasks/{task_id}', response_model=Task, tags=['tasks'])
async def get_task(task_id: int):
    for task in fake_tasks_db:
        if task.id == task_id:
            return task
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail='Task not found'
    )


@app.post('/tasks/', response_model=Task, tags=['tasks'])
async def create_task(task: TaskCreate):
    new_id = max((task.id for task in fake_tasks_db), default=0) + 1

    new_task = Task(
        id=new_id,
        **task.model_dump(),
        created_at=datetime.now(),
        is_completed=False
    )

    fake_tasks_db.append(new_task)

    return new_task
