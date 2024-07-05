from fastapi import APIRouter

from core.settings import settings
from .auth import auth_router
from .users import users_router

v1_router = APIRouter(
    prefix=settings.api.v1.prefix
)

v1_router.include_router(auth_router, prefix=settings.api.v1.auth, tags=["Auth"])
v1_router.include_router(users_router, prefix=settings.api.v1.users, tags=["Users"])
