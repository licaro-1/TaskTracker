from typing import Optional

from sqlalchemy import insert, update, delete, select, Result, func
from core.pagination.utils import format_to_pagination_scheme
from .base import AbstractRepository
from core.db.db_helper import db_helper


class SqlAlchemyRepository(AbstractRepository):
    model = None

    async def create_one(self, data: dict) -> model:
        async with db_helper.session_factory() as session:
            stmt = insert(self.model).values(**data).returning(self.model)
            res: Result = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def get_one(self, **filter_by) -> Optional[model]:
        async with db_helper.session_factory() as session:
            stmt = select(self.model).filter_by(**filter_by)
            res: Result = await session.execute(stmt)
            return res.scalar_one_or_none()

    async def update_one(self, id: int, data: dict) -> model:
        async with db_helper.session_factory() as session:
            stmt = update(self.model).filter_by(id=id).values(**data).returning(self.model)
            res: Result = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def delete_one(self, **filter_by):
        async with db_helper.session_factory() as session:
            stmt = delete(self.model).filter_by(**filter_by)
            await session.execute(stmt)
            await session.commit()

    async def get_multi(
        self,
        limit: int,
        offset: int = 0,
        order: str = "created_at",
        **filter_by,
    ):
        async with db_helper.session_factory() as session:
            stmt = (
                select(self.model)
                .order_by(order)
                .filter_by(**filter_by)
                .limit(limit)
                .offset(offset)
            )
            stmt_pages_count = (select(func.count()).select_from(self.model).filter_by(**filter_by))
            res_pages_count: Result = await session.execute(stmt_pages_count)
            res: Result = await session.execute(stmt)
            pages_count = max(1, res_pages_count.scalar() / limit)
            result = {
                "results": res.scalars(),
                "pages_count": pages_count,
            }
            return result
