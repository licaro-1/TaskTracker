from typing import Annotated

from fastapi import APIRouter, status, Depends, Response

from authentication.auth import get_current_user
from api.dependencies.tasks import tasks_service
from users.models import User
from tasks.schemas import (
    TaskCommentCreate,
    TaskCommentUpdate
)


task_comments_router = APIRouter()


@task_comments_router.post("/{task_id}/", status_code=status.HTTP_201_CREATED)
async def create_task_comment(
    task_id: int,
    comment_data: TaskCommentCreate,
    user: Annotated[User, Depends(get_current_user)]
):
    await tasks_service.create_task_comment(
        task_id=task_id,
        user=user,
        comment_data=comment_data
    )
    return Response(status_code=status.HTTP_201_CREATED)


@task_comments_router.get("/{comment_id}/")
async def get_comment_by_id(comment_id: int, user: Annotated[User, Depends(get_current_user)]):
    return await tasks_service.get_comment_by_id(comment_id=comment_id, user_id=user.id)


@task_comments_router.patch("/{comment_id}/")
async def update_task_comment(
    comment_id: int,
    comment_data: TaskCommentUpdate,
    user: Annotated[User, Depends(get_current_user)]
):
    await tasks_service.update_task_comment(
        comment_id=comment_id,
        user=user,
        upd_comment_data=comment_data
    )
    return Response(status_code=status.HTTP_200_OK)


@task_comments_router.delete("/{comment_id}/")
async def delete_task_comment(
    comment_id: int,
    user: Annotated[User, Depends(get_current_user)]
):
    await tasks_service.delete_task_comment(comment_id=comment_id, user=user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)