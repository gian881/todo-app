import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from data.task import TaskCreate
from data.user import User
from dependencies import DB, get_current_user

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.get("/tasks")
async def get_user_tasks(
        current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return DB.get_tasks_by_user_id(current_user.id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.post('/tasks', status_code=status.HTTP_201_CREATED)
async def create_task(
        current_user: Annotated[User, Depends(get_current_user)],
        name: str,
        description: str,
        alert_datetime: datetime.datetime
):
    task_to_create = TaskCreate(name=name,
                                description=description,
                                alert_date_time=alert_datetime,
                                user_id=current_user.id)
    task_created = DB.create_task(task_to_create)
    return {
        'detail': 'Task created successfully',
        'task': task_created.model_dump_json()
    }
