from typing import TYPE_CHECKING

from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from core.db.base import Base
from core.db.mixins.dt_created_updated_at import DtCreatedAndUpdatedAtMixin

from tasks.models import UserTask

if TYPE_CHECKING:
    from tasks.models import Task, TaskComment


DEFAULT_USER_AVATAR = "default_image.png"


class User(Base, DtCreatedAndUpdatedAtMixin):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(
        String(length=20), unique=True, nullable=False
    )
    first_name: Mapped[str] = mapped_column(String(length=30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(length=30), nullable=False)
    email: Mapped[str] = mapped_column(
        String(length=320), unique=True, index=True, nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    about: Mapped[str] = mapped_column(String(length=340), nullable=True)
    avatar: Mapped[str] = mapped_column(default=DEFAULT_USER_AVATAR, nullable=False)

    @hybrid_property
    def full_name(self):
        return self.first_name + " " + self.last_name

    # relationship
    tasks: Mapped["Task"] = relationship(back_populates="author", foreign_keys="Task.author_id", cascade="all, delete")
    marked_in_tasks: Mapped[list["Task"]] = relationship(
        back_populates="marked_users",
        secondary=UserTask,
        uselist=True,
    )
    comments: Mapped[list["TaskComment"]] = relationship(back_populates="author", uselist=True, cascade="all, delete")
