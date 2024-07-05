from fastapi import APIRouter, status, Response

from core.authentication.schemas import UserLogin, JWTTokenInfo
from users.schemas import UserRead, UserCreate
from api.dependencies.users import users_service


auth_router = APIRouter()


@auth_router.post("/login/", response_model=JWTTokenInfo)
async def login(
    login_data: UserLogin,
):
    return await users_service.login(login_data=login_data)


@auth_router.post("/register/", response_model=UserRead)
async def register(
    register_data: UserCreate
):
    return await users_service.create_user(user_data=register_data)


@auth_router.post("/logout/", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response
):
    return await users_service.logout(response=response)
