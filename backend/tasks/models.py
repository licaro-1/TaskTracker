from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    String,
    ForeignKey,
    Table,
    Column,
    UniqueConstraint,
    Integer,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.db.base import Base
from core.db.mixins.dt_created_updated_at import (
    DtCreatedAndUpdatedAtMixin,
)
from core.db.mixins.int_id_pk import IntIdPkMixin

if TYPE_CHECKING:
    from users.models import User


MAX_TASK_COMMENT_TEXT_LEN = 1000

UserTask = Table(
    "marked_user_tasks",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE")),
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE")),
    UniqueConstraint("user_id", "task_id", name="unique_marked_user"),
)


class TaskStatus(Base, IntIdPkMixin, DtCreatedAndUpdatedAtMixin):
    __tablename__ = "task_statuses"

    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255))
    # relationship
    tasks: Mapped[list["Task"]] = relationship(back_populates="status")


class TaskComment(Base, IntIdPkMixin, DtCreatedAndUpdatedAtMixin):
    __tablename__ = "task_comments"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    text: Mapped[str] = mapped_column(String(MAX_TASK_COMMENT_TEXT_LEN))
    # relationship
    author: Mapped["User"] = relationship(
        back_populates="comments",
        lazy="joined",
        cascade="all, delete",
    )
    task: Mapped["Task"] = relationship(
        back_populates="comments",
        lazy="joined",
        cascade="all, delete",
    )


class Task(Base, IntIdPkMixin, DtCreatedAndUpdatedAtMixin):
    __tablename__ = "tasks"

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status_id: Mapped[int] = mapped_column(
        ForeignKey("task_statuses.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1900))
    # relationship
    status: Mapped["TaskStatus"] = relationship(
        back_populates="tasks", lazy="joined", foreign_keys=[status_id]
    )
    author: Mapped["User"] = relationship(
        back_populates="tasks", foreign_keys=[author_id], lazy="joined"
    )
    marked_users: Mapped[list["User"]] = relationship(
        back_populates="marked_in_tasks",
        secondary=UserTask,
        uselist=True,
        lazy="selectin",
    )
    comments: Mapped[list["TaskComment"]] = relationship(
        back_populates="task", uselist=True
    )
