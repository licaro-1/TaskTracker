from datetime import datetime, timedelta
from typing import Annotated

import jwt
import bcrypt
from jwt import InvalidTokenError

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

import core.exceptions.users as user_exc
from core.settings import settings

http_bearer = HTTPBearer()


async def encode_jwt(
    payload: dict,
    key: str = settings.auth.private_key_patch.read_text(),
    algorithm: str = settings.auth.algorithm,
    expire_min: int = settings.auth.access_token_expire_min,
):
    to_encode = payload.copy()
    now = datetime.utcnow()
    expire = now + timedelta(minutes=expire_min)
    to_encode.update(exp=expire, iat=now)
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
