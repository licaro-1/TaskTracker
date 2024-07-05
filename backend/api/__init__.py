from fastapi import APIRouter

from .v1 import v1_router
from core.settings import settings

router = APIRouter(
    prefix=settings.api.prefix
)

router.include_router(v1_router)