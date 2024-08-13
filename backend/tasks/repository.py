from typing import Optional

from sqlalchemy import update, Result, select, func
from sqlalchemy.orm import selectinload, joinedload

from core.db.db_helper import db_helper

from repositories.sqlalchemy import SqlAlchemyRepository
from .models import Task, TaskStatus, TaskComment, UserTask


class TaskRepository(SqlAlchemyRepository):
    model = Task

    async def create_one(self, data: dict) -> model:
        async with db_helper.session_factory() as session:
            marked_users = data.pop("marked_users")
            task = Task(**data)
            session.add(task)
            task.marked_users = marked_users
            await session.commit()
            await session.refresh(task)
        return task

    async def update_one(self, id: int, upd_data: dict) -> model:
        async with db_helper.session_factory() as session:
            task = await session.get(self.model, id)
            new_marked_users = upd_data.pop("marked_users")
            for key, val in upd_data.items():
                setattr(task, key, val)
            task.marked_users.clear()
            # for user in task.marked_users:
            #     if user not in new_marked_users:
            #         task.marked_users.remove(user)
            #     else:
            #         new_marked_users.remove(user)
            await session.commit()
            await session.refresh(task)
            if new_marked_users:
                for user in new_marked_users:
                    task.marked_users.append(user)
            await session.commit()
            await session.refresh(task)
            return task

    async def get_tasks_user_is_marked(
        self,
        limit: int,
        user_id: int,
        offset: int = 0,
        order: str = "created_at",
    ):
        async with db_helper.session_factory() as session:
            subq = (
                select(UserTask.c.task_id)
                .filter_by(user_id=user_id)
                .subquery()
            )
            stmt = (
                select(self.model)
                .where(self.model.id.in_(select(subq)))
                .order_by(order)
                .limit(limit)
                .offset(offset)
            )
            stmt_pages_count = (select(func.count()).select_from(self.model).where(self.model.id.in_(select(subq))))
            res_pages_count: Result = await session.execute(stmt_pages_count)
            res: Result = await session.execute(stmt)
            pages_count = max(1, res_pages_count.scalar() / limit)
            result = {
                "results": res.scalars(),
                "pages_count": pages_count,
            }
            return result

    async def get_task_with_comments(
            self,
            **filter_by
    ) -> Optional[model]:
        async with db_helper.session_factory() as session:
            stmt = (
                select(self.model)
                .options(selectinload(self.model.comments).joinedload(TaskComment.author))
                .filter_by(**filter_by)
            )
            res: Result = await session.execute(stmt)
            task = res.scalar_one_or_none()
            return task


class TaskStatusRepository(SqlAlchemyRepository):
    model = TaskStatus

    async def get_all(self):
        async with (db_helper.session_factory() as session):
            stmt = (
                select(self.model)
            )
            res: Result = await session.execute(stmt)
            return res.scalars().all()

    async def delete_one(self, **filter_by):
        async with (db_helper.session_factory() as session):
            status_open = await self.get_one(slug="open")
            status_to_delete = await self.get_one(**filter_by)
            stmt_update_tasks_to_open_status = (
                update(Task)
                .filter_by(status_id=status_to_delete.id)
                .values(status_id=status_open.id)
            )
            await session.execute(stmt_update_tasks_to_open_status)
            await session.commit()
            return await super().delete_one(**filter_by)


class TaskCommentRepository(SqlAlchemyRepository):
    model = TaskComment

    async def get_one(self, **filter_by) -> Optional[model]:
        async with db_helper.session_factory() as session:
            stmt = (
                select(self.model)
                .options(
                    joinedload(self.model.author),
                    joinedload(self.model.task))
                .filter_by(**filter_by)
            )
            res: Result = await session.execute(stmt)
            return res.scalar_one_or_none()
