import uuid
from datetime import datetime, timedelta
from typing import Annotated

import jwt
import bcrypt
from jwt import InvalidTokenError

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import core.exceptions.users as user_exc
from core.settings import settings
from users.models import User

http_bearer = HTTPBearer()

TOKEN_TYPE = "type"
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


async def create_jwt(
    token_type: str,
    payload: dict,
    expire_minutes: int = settings.auth.access_token_expire_min,
    expire_timedelta: timedelta | None = None,
) -> str:
    jwt_payload = {TOKEN_TYPE: token_type}
    jwt_payload.update(payload)
    return await encode_jwt(
        payload=jwt_payload,
        expire_min=expire_minutes,
        expire_timedelta=expire_timedelta
    )


async def create_access_token(user: User) -> str:
    payload = {"sub": user.id, "username": user.username}
    token = await create_jwt(
        token_type=ACCESS_TOKEN_TYPE,
        payload=payload,
        expire_minutes=settings.auth.access_token_expire_min
    )
    return token


async def create_refresh_token(user: User) -> str:
    payload = {"sub": user.id}
    token = await create_jwt(
        token_type=REFRESH_TOKEN_TYPE,
        payload=payload,
        expire_timedelta=timedelta(days=settings.auth.refresh_token_expire_days)
    )
    return token


async def encode_jwt(
    payload: dict,
    key: str = settings.auth.private_key_patch.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_min: int = settings.auth.access_token_expire_min,
    expire_timedelta: timedelta | None = None,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    if expire_timedelta:
        expire = now + expire_timedelta
    else:
        expire = now + timedelta(minutes=expire_min)
    to_encode.update(exp=expire, iat=now, jti=str(uuid.uuid4()))
    encoded = jwt.encode(payload=to_encode, key=key, algorithm=algorithm)
    return encoded


async def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth.public_key_patch.read_text(),
    algorithm: str = settings.auth.algorithm,
):
    try:
        decoded = jwt.decode(jwt=token, key=public_key, algorithms=algorithm)
    except InvalidTokenError:
        raise user_exc.UnauthorizedError
    return decoded


async def get_token_payload(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]):
    token = credentials.credentials
    if not token:
        raise user_exc.UnauthorizedError
    payload = await decode_jwt(token=token)
    return payload


async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


async def validate_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        password=password.encode(), hashed_password=hashed_password.encode()
    )
