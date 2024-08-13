from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column


class DtCreatedAtMixin:
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())


class DtUpdatedAtMixin:
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow(), onupdate=func.now()
    )


class DtCreatedAndUpdatedAtMixin(DtCreatedAtMixin, DtUpdatedAtMixin):
    pass
