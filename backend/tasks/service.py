from notifications.notification import (
    send_new_task_comment_notify,
    send_added_to_the_marked_users_notify,
)
from logs.get_logger import logger
import core.exceptions.tasks as tasks_exc
from core.pagination.schemas import PaginationParams, PageResponse
from core.pagination.utils import format_to_pagination_scheme
from users.models import User
from tasks.models import Task, MAX_TASK_COMMENT_TEXT_LEN
from .schemas import (
    TaskRead,
    TaskCreate,
    TaskStatusCreate,
    TaskStatusRead,
    TaskStatusUpdate,
    TaskUpdate,
    TaskWithCommentsRead,
    TaskCommentCreate,
    TaskCommentUpdate,
    TaskCommentRead,
)


class TaskService:
    def __init__(
        self,
        task_repository,
        task_status_repository,
        user_repository,
        task_comment_repository,
    ):
        self.task_repository = task_repository()
        self.task_statuses_repository = task_status_repository()
        self.users_repository = user_repository()
        self.task_comment_repository = task_comment_repository()

    async def is_superuser_or_task_author(self, task: Task, user: User):
        return user.is_superuser or task.author_id == user.id

    async def is_superuser_task_author_or_marked_user(self, task: Task, user: User):
        marked_users_ids = [marked_user.id for marked_user in task.marked_users]
        return (
            await self.is_superuser_or_task_author(task=task, user=user)
            or user.id in marked_users_ids
        )

    async def get_list_of_marked_users(self, new_marked_users: list[str]) -> list[User]:
        result_marked_users_list = []
        for username in new_marked_users:
            user = await self.users_repository.get_one(username=username)
            if not user:
                raise tasks_exc.MarkedUserNotFoundError(username)
            result_marked_users_list.append(user)
        return result_marked_users_list

    async def create_task(self, author: User, task_data: TaskCreate):
        logger.debug(
            f"Start creating task by user({author.id!r}) with data: {task_data}."
        )
        if author.username in task_data.marked_users:
            logger.info(f"Task creating error, author mark yourself in marked_users.")
            raise tasks_exc.TaskAddSelfToMarkedUsersError
        task_data = task_data.model_dump()
        open_status = await self.task_statuses_repository.get_one(slug="open")
        task_data["author_id"] = author.id
        task_data["status_id"] = open_status.id
        if task_data["marked_users"]:
            task_data["marked_users"] = await self.get_list_of_marked_users(
                new_marked_users=task_data["marked_users"]
            )
        task = await self.task_repository.create_one(task_data)
        logger.info(f"Task({task.id}) created successfully.")
        for user in task.marked_users:
            logger.info(f"Start send email notify to {user.email}")
            send_added_to_the_marked_users_notify.delay(
                to_user_email=user.email,
                task_author_full_name=task.author.full_name,
                task_title=task.title,
                task_description=task.description,
            )
        return TaskRead.model_validate(task, from_attributes=True)

    async def update_task(self, author: User, task_id: int, upt_data: TaskUpdate):
        task = await self.task_repository.get_one(id=task_id)
        logger.info(f"Start updating task({task_id!r}), new_data: {upt_data}")
        if task.author_id != author.id:
            logger.info(f"Update task({task_id!r}) error, user is not task author")
            raise tasks_exc.NotAuthorOfTaskUpdateError
        if author.username in upt_data.marked_users:
            logger.info(
                f"Update task({task_id!r}) error, user mark yourself in marked_users"
            )
            raise tasks_exc.TaskSelfMarkUpdateError
        status = await self.task_statuses_repository.get_one(id=upt_data.status_id)
        if not status:
            logger.info(
                f"Update task({task_id!r}) error, specified status({upt_data.status_id}) was not found"
            )
            raise tasks_exc.StatusNotFound(upt_data.status_id)
        upt_data = upt_data.model_dump()
        if upt_data["marked_users"]:
            upt_data["marked_users"] = await self.get_list_of_marked_users(
                new_marked_users=upt_data["marked_users"]
            )
        task_marked_users_email = [user.email for user in task.marked_users]
        upt_task = await self.task_repository.update_one(id=task_id, upd_data=upt_data)
        # send email for new marked users
        logger.info(f"Task({task_id!r}) updated successfully")
        for user in upt_task.marked_users:
            if user.email not in task_marked_users_email:
                logger.info(f"Start send email notify to {user.email}")
                send_added_to_the_marked_users_notify.delay(
                    to_user_email=user.email,
                    task_author_full_name=task.author.full_name,
                    task_title=task.title,
                    task_description=task.description,
                )
        return TaskRead.model_validate(upt_task, from_attributes=True)

    async def delete_task(self, task_id: int, user: User) -> None:
        task = await self.task_repository.get_one(id=task_id)
        if not task:
            raise tasks_exc.TaskNotFoundError
        logger.info(f"Start deleting task({task_id!r})")
        if not await self.is_superuser_or_task_author(task=task, user=user):
            logger.info(
                f"Task deleting error, user({user.id!r}) not author or superuser"
            )
            raise tasks_exc.NotTaskAuthorDeleteError
        await self.task_repository.delete_one(id=task_id)
        logger.info(f"Task({task_id!r}) delete successfully")

    async def get_tasks_by_user(
        self,
        user_id: int,
        pagination_params: PaginationParams,
        order: str = "created_at",
    ) -> PageResponse:
        page, limit = pagination_params.page, pagination_params.limit
        offset = (page - 1) * limit
        res = await self.task_repository.get_multi(
            limit=limit, offset=offset, order=order, author_id=user_id
        )
        return format_to_pagination_scheme(
            results=[
                TaskRead.model_validate(task, from_attributes=True)
                for task in res["results"]
            ],
            pages_count=res["pages_count"],
            page=page,
            limit=limit,
        )

    async def get_user_marked_tasks(
        self,
        user: User,
        pagination_params: PaginationParams,
        order: str = "created_at",
    ) -> PageResponse:
        page, limit = pagination_params.page, pagination_params.limit
        offset = (page - 1) * limit
        res = await self.task_repository.get_tasks_user_is_marked(
            offset=offset, limit=limit, user_id=user.id, order=order
        )
        return format_to_pagination_scheme(
            results=[
                TaskRead.model_validate(task, from_attributes=True)
                for task in res["results"]
            ],
            pages_count=res["pages_count"],
            page=page,
            limit=limit,
        )

    async def get_task_by_id(self, user_id: int, task_id: int) -> TaskRead:
        task = await self.task_repository.get_one(id=task_id)
        if not task:
            raise tasks_exc.TaskNotFoundError
        if user_id != task.author_id and user_id not in [
            user.id for user in task.marked_users
        ]:
            raise tasks_exc.TaskReadPermissionDeniedError
        return TaskRead.model_validate(task, from_attributes=True)

    async def get_task_with_comments(
        self, user: User, **filter_by
    ) -> TaskWithCommentsRead:
        task = await self.task_repository.get_task_with_comments(**filter_by)
        if not task:
            raise tasks_exc.TaskNotFoundError
        if not await self.is_superuser_task_author_or_marked_user(user=user, task=task):
            raise tasks_exc.TaskReadPermissionDeniedError
        return TaskWithCommentsRead.model_validate(task, from_attributes=True)

    async def create_task_comment(
        self, task_id: int, user: User, comment_data: TaskCommentCreate
    ) -> None:
        task = await self.task_repository.get_task_with_comments(id=task_id)
        if not task:
            raise tasks_exc.TaskNotFoundError
        logger.info(
            f"Start creating comment for task({task.id!r}) with text:{comment_data.text!r} by user({user.id!r})"
        )
        if len(comment_data.text) > MAX_TASK_COMMENT_TEXT_LEN:
            logger.info(
                f"Comment creating error, len comment text more than {MAX_TASK_COMMENT_TEXT_LEN} symbols"
            )
            raise tasks_exc.CommentCreateLenError()
        if user.id != task.author_id and user.id not in [
            user.id for user in task.marked_users
        ]:
            logger.info(f"Comment creating error, user not author or marked user")
            raise tasks_exc.NotAuthorOrMarkedUserAddCommentError
        comment_data_to_create = comment_data.model_dump()
        comment_data_to_create["author_id"] = user.id
        comment_data_to_create["task_id"] = task.id
        comment = await self.task_comment_repository.create_one(comment_data_to_create)
        logger.info(f"Comment to task({task_id!r}) created successfully")
        comment_notify = await self.task_comment_repository.get_one(id=comment.id)
        if comment.author_id != task.author_id:
            logger.info(f"Start send email notify to {task.author.email}")
            send_new_task_comment_notify.delay(
                to_user_email=task.author.email,
                comment_author_full_name=comment_notify.author.full_name,
                comment_text=comment_notify.text,
                task_title=task.title,
            )

    async def get_comment_by_id(self, comment_id: int, user_id: int) -> TaskCommentRead:
        comment = await self.task_comment_repository.get_one(id=comment_id)
        if not comment:
            raise tasks_exc.CommentNotFoundError
        if comment.author_id != user_id:
            raise tasks_exc.NotAuthorCommentReadError
        return TaskCommentRead.model_validate(comment, from_attributes=True)

    async def update_task_comment(
        self, user: User, comment_id: int, upd_comment_data: TaskCommentUpdate
    ) -> None:
        comment = await self.task_comment_repository.get_one(id=comment_id)
        if not comment:
            raise tasks_exc.CommentNotFoundError
        logger.info(
            f"Start updating comment({comment_id!r}), upd_data: {upd_comment_data!r}"
        )
        if comment.author_id != user.id:
            logger.info(
                f"Updating error, user({user.id!r}) is not author of comment({comment_id!r})"
            )
            raise tasks_exc.NotAuthorCommentUpdateError
        await self.task_comment_repository.update_one(
            id=comment_id, data=upd_comment_data.model_dump()
        )
        logger.info(f"Comment({comment_id!r}) updated successfully by user({user.id})")

    async def delete_task_comment(
        self,
        user: User,
        comment_id,
    ) -> None:
        comment = await self.task_comment_repository.get_one(id=comment_id)
        if not comment:
            raise tasks_exc.CommentNotFoundError
        logger.info(f"Start deleting comment({comment_id!r}) by user({user.id!r})")
        if user.id != comment.author_id and not user.is_superuser:
            logger.info(
                f"Comment deleting error, user({user.id}) not author or superuser"
            )
            raise tasks_exc.NotAuthorDeleteCommentError
        await self.task_comment_repository.delete_one(id=comment_id)
        logger.info(f"Comment({comment_id!r}) deleted successfully by user({user.id})")

    async def add_task_status(
        self, user: User, data: TaskStatusCreate
    ) -> TaskStatusRead:
        logger.info(
            f"Start creating task status with data: {data!r} by user({user.id})"
        )
        if not user.is_superuser:
            logger.info(
                f"Task status creating error, user({user.id!r}) is not superuser"
            )
            raise tasks_exc.NotSuperUserStatusCreateDeleteUpdateError
        task_status = await self.task_statuses_repository.create_one(data.model_dump())
        logger.info(f"Task status created successfully id=({task_status.id})")
        return TaskStatusRead.model_validate(task_status, from_attributes=True)

    async def get_task_statuses(self) -> list[TaskStatusRead]:
        task_statuses = await self.task_statuses_repository.get_all()
        return task_statuses

    async def update_task_status(
        self, user: User, status_id: int, data: TaskStatusUpdate
    ) -> TaskStatusRead:
        logger.info(
            f"Start updating task status({status_id!r}) with data: {data!r} by user({user.id})"
        )
        if not user.is_superuser:
            logger.info(
                f"Task status({status_id!r}) updating error, user({user.id}) is not superuser"
            )
            raise tasks_exc.NotSuperUserStatusCreateDeleteUpdateError
        upd_status = await self.task_statuses_repository.update_one(
            data=data.model_dump(exclude_unset=True), id=status_id
        )
        logger.info(
            f"Task status({status_id!r}) updated successfully. data: {upd_status!r}"
        )
        return TaskStatusRead.model_validate(upd_status, from_attributes=True)

    async def delete_task_status(self, user: User, status_id: int):
        logger.info(f"Start deleting task status({status_id!r}) by user({user.id})")
        if not user.is_superuser:
            logger.info(
                f"Task status({status_id!r}) deleting error, user({user.id}) is not superuser"
            )
            raise tasks_exc.NotSuperUserStatusCreateDeleteUpdateError
        status = await self.task_statuses_repository.get_one(id=status_id)
        if not status:
            logger.info(f"Task status({status_id!r}) deleting error, status not found")
            raise tasks_exc.StatusNotFound(status_id)
        await self.task_statuses_repository.delete_one(id=status_id)
        logger.info(f"Task status({status_id!r}) deleted successfully")
