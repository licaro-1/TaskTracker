from typing import Annotated

from fastapi import APIRouter, status, Response, Depends

from api.dependencies.pagination import get_pagination_params
from api.dependencies.tasks import tasks_service
from authentication.auth import get_current_user
from tasks.schemas import TaskRead, TaskCreate, TaskUpdate, TaskWithCommentsRead
from users.models import User
from core.pagination.schemas import PageResponse, PaginationParams


tasks_router = APIRouter()


@tasks_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate, user: Annotated[User, Depends(get_current_user)]
):
    return await tasks_service.create_task(author=user, task_data=data)


@tasks_router.get("/marked-in-tasks/", response_model=PageResponse)
async def get_marked_in_tasks(
    pagination_params: Annotated[PaginationParams, Depends(get_pagination_params)],
    user: Annotated[User, Depends(get_current_user)],
):
    return await tasks_service.get_user_marked_tasks(user, pagination_params)


@tasks_router.get("/{task_id}/", response_model=TaskWithCommentsRead)
async def get_task(task_id: int, user: Annotated[User, Depends(get_current_user)]):
    return await tasks_service.get_task_with_comments(user=user, id=task_id)


@tasks_router.get("/", response_model=PageResponse)
async def get_tasks(
    pagination_params: Annotated[PaginationParams, Depends(get_pagination_params)],
    user: Annotated[User, Depends(get_current_user)],
):
    return await tasks_service.get_tasks_by_user(
        user_id=user.id, pagination_params=pagination_params
    )


@tasks_router.put("/{task_id}/", response_model=TaskRead)
async def update_task(
    task_id: int, upd_data: TaskUpdate, user: Annotated[User, Depends(get_current_user)]
):
    return await tasks_service.update_task(
        author=user, task_id=task_id, upt_data=upd_data
    )


@tasks_router.delete("/{task_id}/")
async def delete_task(task_id: int, user: Annotated[User, Depends(get_current_user)]):
    await tasks_service.delete_task(task_id=task_id, user=user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
