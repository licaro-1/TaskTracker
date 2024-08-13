from fastapi import APIRouter

from core.settings import settings
from .auth import auth_router
from .users import users_router
from .tasks import tasks_router
from .task_statuses import task_statuses_router
from .task_comments import task_comments_router
v1_router = APIRouter(
    prefix=settings.api.v1.prefix
)

v1_router.include_router(auth_router, prefix=settings.api.v1.auth, tags=["Auth"])
v1_router.include_router(users_router, prefix=settings.api.v1.users, tags=["Users"])
v1_router.include_router(task_statuses_router, prefix=settings.api.v1.task_statuses, tags=["Task Statuses"])
v1_router.include_router(task_comments_router, prefix=settings.api.v1.task_comments, tags=["Task Comments"])
v1_router.include_router(tasks_router, prefix=settings.api.v1.tasks, tags=["Tasks"])
