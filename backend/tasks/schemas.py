from typing import Optional

from pydantic import BaseModel
from datetime import datetime

from users.schemas import UserRead


# TaskStatus
class TaskStatusBase(BaseModel):
    name: str
    slug: str


class TaskStatusCreate(TaskStatusBase):
    ...


class TaskStatusRead(TaskStatusBase):
    id: int


class TaskStatusUpdate(TaskStatusBase):
    name: Optional[str] = None
    slug: Optional[str] = None


# TaskComment
class TaskCommentBase(BaseModel):
    text: str


class TaskCommentRead(TaskCommentBase):
    id: int
    author: UserRead
    created_at: datetime
    text: str


class TaskCommentCreate(TaskCommentBase):
    pass


class TaskCommentUpdate(TaskCommentBase):
    pass


# Task
class TaskBase(BaseModel):
    title: str
    description: str


class TaskCreate(TaskBase):
    marked_users: list[str]


class TaskRead(TaskBase):
    id: int
    author: UserRead
    status: TaskStatusRead
    marked_users: list[UserRead]
    created_at: datetime
    updated_at: datetime


class TaskWithCommentsRead(TaskRead):
    comments: list[TaskCommentRead]


class TaskUpdate(TaskCreate):
    status_id: int

