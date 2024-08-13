from fastapi import Depends

from users.models import User
from .utils import get_token_payload, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE
from .validation.token_validator import validate_token_type
from api.dependencies.users import users_service
from core.exceptions import users as user_exc


async def get_user_by_token_sub(payload: dict) -> User:
    user = await users_service.get_user_by_id(id=payload.get("sub"))
    if not user:
        raise user_exc.UnauthorizedError
    return user


async def get_current_user(
    payload: dict = Depends(get_token_payload),
) -> User:
    await validate_token_type(payload, ACCESS_TOKEN_TYPE)
    return await get_user_by_token_sub(payload)


async def get_current_user_for_refresh(payload: dict = Depends(get_token_payload)):
    await validate_token_type(payload, REFRESH_TOKEN_TYPE)
    return await get_user_by_token_sub(payload)
