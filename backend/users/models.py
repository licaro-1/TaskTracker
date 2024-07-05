from sqlalchemy import String, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from core.db.base import Base
from core.mixins.dt_created_updated_at import DtCreatedAndUpdatedAt


class User(Base, DtCreatedAndUpdatedAt):
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
    avatar: Mapped[str] = mapped_column(default=None, nullable=True)

    @hybrid_property
    def full_name(self):
        return self.first_name + " " + self.last_name
