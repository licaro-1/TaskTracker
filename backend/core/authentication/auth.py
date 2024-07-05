from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.db_helper import db_helper
from users.models import User

from .utils import get_token_payload
from api.dependencies.users import users_service
from core.exceptions import users as user_exc


async def get_current_user(
    payload: dict = Depends(get_token_payload),
) -> User:
    try:
        user = await users_service.get_user(id=payload.get("sub"))
    except user_exc.UserNotFoundError:
        raise user_exc.UnauthorizedError
    return user
