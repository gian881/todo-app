import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from data.exceptions import TaskNotFoundException
from data.task import TaskCreate, Task, TaskUpdate
from data.user import User
from dependencies import get_current_user, get_db

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
)


@router.get("")
async def get_user_tasks(
        current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        return get_db().get_tasks_by_user_id(current_user.id)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.post('', status_code=status.HTTP_201_CREATED, response_model=Task)
async def create_task(
        current_user: Annotated[User, Depends(get_current_user)],
        name: str,
        description: str | None = None,
        alert_datetime: datetime.datetime | None = None
):
    task_to_create = TaskCreate(name=name,
                                description=description,
                                alert_date_time=alert_datetime,
                                user_id=current_user.id)
    task_created = get_db().create_task(task_to_create)
    return Task.from_task_in_db(task_created)


@router.delete('', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_id: str
):
    try:
        task = get_db().get_task_by_id(task_id)
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have permission to delete this task."
            )
        get_db().delete_task(task_id)
    except TaskNotFoundException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )


@router.put('', status_code=status.HTTP_200_OK, response_model=Task)
async def update_task(
        current_user: Annotated[User, Depends(get_current_user)],
        task_id: int,
        name: str | None = None,
        description: str | None = None,
        alert_datetime: datetime.datetime | None = None,
        done: bool | None = None
):
    try:
        task = get_db().get_task_by_id(task_id)
        if task.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You don't have permission to edit this task."
            )

        updated_task = get_db().update_task(
            TaskUpdate(
                id=task_id,
                name=name,
                description=description,
                alert_date_time=alert_datetime,
                done=done
            )
        )

        return Task.from_task_in_db(updated_task).model_dump()
    except TaskNotFoundException as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error)
        )
