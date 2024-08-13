from typing import Annotated

from fastapi import APIRouter, status, Depends

from authentication.schemas import UserLogin, JWTTokenInfo
from authentication.auth import get_current_user_for_refresh
from users import User
from users.schemas import UserRead, UserCreate
from api.dependencies.users import users_service


auth_router = APIRouter()


@auth_router.post("/login/", response_model=JWTTokenInfo)
async def login(
    login_data: UserLogin,
):
    return await users_service.login(login_data=login_data)


@auth_router.post("/register/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    register_data: UserCreate
):
    return await users_service.create_user(user_data=register_data)


@auth_router.post("/refresh/", response_model=JWTTokenInfo, response_model_exclude_none=True)
async def refresh_jwt_token(
    user: Annotated[User, Depends(get_current_user_for_refresh)]
):
    return await users_service.refresh_token(user=user)
