from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class DtCreatedAt:
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), server_default=func.now()
    )


class DtUpdatedAt:
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(),
        onupdate=datetime.utcnow(),
        server_onupdate=func.now(),
    )


class DtCreatedAndUpdatedAt(DtCreatedAt, DtUpdatedAt):
    pass