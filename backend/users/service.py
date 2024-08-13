import os
from uuid import uuid4
from typing import Type, Optional

from fastapi import UploadFile
from logs.get_logger import logger

from authentication.schemas import UserLogin, JWTTokenInfo
from core.settings import STATIC_USER_IMAGES_ROOT
from users.models import User, DEFAULT_USER_AVATAR
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
from authentication.validation.password_validator import validate_create_password
from authentication.utils import (
    validate_password,
    create_access_token,
    create_refresh_token,
)
from repositories.base import AbstractRepository


class UserService:
    def __init__(self, users_repository: Type[AbstractRepository]):
        self.users_repository = users_repository()

    async def create_user(self, user_data: UserCreate):
        logger.debug(f"Start creating user, data: {user_data}")
        if await self.users_repository.get_one(email=user_data.email):
            logger.info(f"Create error, email: {user_data.email} already registered")
            raise user_exc.EmailAlreadyRegisteredError
        if await self.users_repository.get_one(username=user_data.username):
            logger.info(
                f"Create error, username: {user_data.username} already registered"
            )
            raise user_exc.UsernameAlreadyRegisteredError
        await validate_create_password(user_data.password)
        data = user_data.model_dump()
        user = await self.users_repository.create_one(data)
        logger.info("User was created successfully")
        return UserRead.model_validate(user, from_attributes=True)

    async def get_users(
        self, pagination_params: PaginationParams, order: str = "created_at"
    ) -> PageResponse:
        page, limit = pagination_params.page, pagination_params.limit
        offset = (page - 1) * limit
        res = await self.users_repository.get_multi(
            limit=limit, offset=offset, order=order
        )
        return format_to_pagination_scheme(
            results=[
                UserRead.model_validate(user, from_attributes=True)
                for user in res["results"]
            ],
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

    async def get_user_by_id(self, id: int) -> Optional[User]:
        user = await self.users_repository.get_one(id=id)
        return user

    async def update_user(self, user_id: int, data: UserUpdate) -> UserRead:
        logger.debug(f"Start update user({user_id!r}) with data: {data}")
        if data.email and await self.users_repository.get_one(email=data.email):
            logger.info(
                f"User({user_id!r}) update error, email: {data.email} already registered"
            )
            raise users_exc.EmailAlreadyRegisteredError
        if data.username and await self.users_repository.get_one(
            username=data.username
        ):
            logger.info(
                f"User update error, username: {data.username!r} already registered"
            )
            raise user_exc.UsernameAlreadyRegisteredError
        data_to_upd = data.model_dump(exclude_unset=True)
        upd_user = await self.users_repository.update_one(id=user_id, data=data_to_upd)
        logger.info(f"Success update user({user_id!r})")
        return UserRead.model_validate(upd_user, from_attributes=True)

    async def login(self, login_data: UserLogin) -> JWTTokenInfo:
        logger.debug(f"Start login user with data: {login_data}")
        user = await self.users_repository.get_one(email=login_data.email)
        if not user:
            logger.info(f"Login error, user with email: {login_data.email} not found")
            raise user_exc.InvalidLoginDataError
        if not await validate_password(
            login_data.password, hashed_password=user.hashed_password
        ):
            logger.info(f"Login error, user entered an incorrect password")
            raise user_exc.InvalidLoginDataError
        access_token = await create_access_token(user)
        refresh_token = await create_refresh_token(user)
        return JWTTokenInfo(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_token(self, user: User) -> JWTTokenInfo:
        logger.info(f"Refreshing token for user({user.id})")
        access_token = await create_access_token(user)
        logger.info(f"New access token for user({user.id}) - {access_token}")
        return JWTTokenInfo(
            access_token=access_token,
        )

    async def update_avatar(self, user: User, image: UploadFile) -> UserRead:
        logger.debug(f"Start update user({user.id}) avatar")
        if user.avatar != DEFAULT_USER_AVATAR:
            # removing user avatar from statis file
            logger.info(f"remove user avatar {user.avatar}")
            os.remove(STATIC_USER_IMAGES_ROOT + user.avatar)
        file_name = str(uuid4()) + image.filename[-6:]
        file_path = STATIC_USER_IMAGES_ROOT + file_name
        with open(file_path, "wb") as f:
            f.write(image.file.read())
        res = await self.users_repository.update_one(
            id=user.id, data={"avatar": file_name}
        )
        logger.info(f"Update user({user.id}) avatar to {file_name}")
        return UserRead.model_validate(res, from_attributes=True)
