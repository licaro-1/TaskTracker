from typing import Annotated

from fastapi import APIRouter, status, Depends, UploadFile

from api.dependencies.pagination import get_pagination_params
from api.dependencies.users import users_service
from authentication.auth import get_current_user
from users.schemas import (
    UserRead,
    UserUpdate,
    UserProfileRead,
)
from users.models import User
from core.pagination.schemas import PageResponse, PaginationParams


users_router = APIRouter()


@users_router.get("/", response_model=PageResponse)
async def get_users(
    pagination_params: Annotated[PaginationParams, Depends(get_pagination_params)]
):
    return await users_service.get_users(pagination_params)


@users_router.get("/@{username}/", response_model=UserRead)
async def get_user_by_username(
    username: str
):
    return await users_service.get_user(username=username)


@users_router.get("/me/", response_model=UserProfileRead)
async def get_profile(
    user: Annotated[User, Depends(get_current_user)]
):
    return await users_service.get_profile(user.id)


@users_router.patch("/me/", response_model=UserRead)
async def update_profile(
    user: Annotated[User, Depends(get_current_user)],
    user_data: UserUpdate
):
    return await users_service.update_user(user_id=user.id, data=user_data)


@users_router.patch("/me/update-avatar/", status_code=status.HTTP_200_OK)
async def update_profile_avatar(
    user: Annotated[User, Depends(get_current_user)],
    image: UploadFile
):
    return await users_service.update_avatar(user, image)