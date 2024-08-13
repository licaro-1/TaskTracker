from typing import Annotated

from fastapi import APIRouter, Depends, status

from authentication.auth import get_current_user
from users import User
from api.dependencies.tasks import tasks_service
from tasks.schemas import (
    TaskStatusRead,
    TaskStatusCreate,
    TaskStatusUpdate
)

task_statuses_router = APIRouter()


@task_statuses_router.post("/", response_model=TaskStatusRead, status_code=status.HTTP_201_CREATED)
async def create_task_status(user: Annotated[User, Depends(get_current_user)], data: TaskStatusCreate):
    return await tasks_service.add_task_status(user=user, data=data)


@task_statuses_router.get("/", response_model=list[TaskStatusRead])
async def get_task_statuses():
    return await tasks_service.get_task_statuses()


@task_statuses_router.patch("/{status_id}/", response_model=TaskStatusRead)
async def update_task_statuses(
    user: Annotated[User, Depends(get_current_user)],
    status_id: int,
    upd_data: TaskStatusUpdate
):
    return await tasks_service.update_task_status(status_id=status_id, user=user, data=upd_data)


@task_statuses_router.delete("/{status_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_status(user: Annotated[User, Depends(get_current_user)], status_id: int):
    return await tasks_service.delete_task_status(status_id=status_id, user=user)
