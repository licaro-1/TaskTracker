import os
from uuid import uuid4

from typing import Type

from fastapi import Response, UploadFile

from core.authentication.schemas import UserLogin, JWTTokenInfo
from core.settings import settings, STATIC_USER_IMAGES_ROOT
from users.models import User
from users.schemas import (
    UserRead,
    UserCreate,
    UserUpdate,
    UserProfileRead,
)
from core.exceptions import users as users_exc
from core.pagination.schemas import PaginationParams, PageResponse
from core.pagination.utils import format_to_pagination_scheme
from core.exceptions import users as user_exc
from core.authentication.password_validator import validate_create_password
from core.authentication.utils import hash_password, validate_password, encode_jwt

from repositories.base import AbstractRepository


class UserService:
    def __init__(self, users_repository: Type[AbstractRepository]):
        self.users_repository = users_repository()

    async def create_user(self, user_data: UserCreate):
        if await self.users_repository.get_one(email=user_data.email):
            raise user_exc.EmailAlreadyRegisteredError
        if await self.users_repository.get_one(username=user_data.username):
            raise user_exc.UsernameAlreadyRegisteredError
        await validate_create_password(user_data.password)
        hashed_password = await hash_password(user_data.password)
        data = user_data.model_dump()
        data.pop("password")
        data["hashed_password"] = hashed_password
        user = await self.users_repository.create_one(data)
        return UserRead.model_validate(user, from_attributes=True)

    async def get_users(
        self,
        pagination_params: PaginationParams,
        order: str = "created_at"
    ) -> PageResponse:
        page, limit = pagination_params.page, pagination_params.limit
        offset = (page - 1) * limit
        res = await self.users_repository.get_multi(
            limit=limit,
            offset=offset,
            order=order
        )
        return format_to_pagination_scheme(
            results=[UserRead.model_validate(user, from_attributes=True) for user in res["results"]],
            pages_count=res["pages_count"],
            page=page,
            limit=limit,
        )

    async def get_profile(self, user_id: int) -> UserProfileRead:
        user: User = await self.users_repository.get_one(id=user_id)
        return UserProfileRead.model_validate(user, from_attributes=True)

    async def get_user(self, **filter_by) -> UserRead:
        user: User = await self.users_repository.get_one(**filter_by)
        if not user:
            raise user_exc.UserNotFoundError
        return UserRead.model_validate(user, from_attributes=True)

    async def update_user(self, user_id: int, data: UserUpdate) -> UserRead:
        if data.email and await self.users_repository.get_one(email=data.email):
            raise users_exc.EmailAlreadyRegisteredError
        if data.username and await self.users_repository.get_one(username=data.username):
            raise user_exc.UsernameAlreadyRegisteredError
        data_to_upd = data.model_dump(exclude_unset=True)
        upd_user = await self.users_repository.update_one(id=user_id, data=data_to_upd)
        return UserRead.model_validate(upd_user, from_attributes=True)

    async def login(self, login_data: UserLogin) -> JWTTokenInfo:
        user = await self.users_repository.get_one(email=login_data.email)
        if not user:
            raise user_exc.InvalidLoginDataError
        if not await validate_password(
                login_data.password,
                hashed_password=user.hashed_password):
            raise user_exc.InvalidLoginDataError
        jwt_payload = {"sub": user.id, "username": user.username}
        token = await encode_jwt(jwt_payload)
        return JWTTokenInfo(
            access_token=token,
            token_type=settings.auth.token_type
        )

    async def logout(self, response: Response):
        return response.delete_cookie(settings.auth.cookie_session_key)

    async def update_avatar(self, user: User, image: UploadFile) -> UserRead:
        if user.avatar:
            # removing user avatar from statis file
            os.remove(STATIC_USER_IMAGES_ROOT + user.avatar)
        file_name = str(uuid4()) + image.filename[-6:]
        file_path = STATIC_USER_IMAGES_ROOT + file_name
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        res = await self.users_repository.update_one(id=user.id, data={"avatar": file_name})
        return UserRead.model_validate(res, from_attributes=True)
