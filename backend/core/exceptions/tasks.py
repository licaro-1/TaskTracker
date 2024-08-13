from fastapi import status

from .base import BaseException


class TaskNotFoundError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "Task not found"


class NotTaskAuthorDeleteError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You are not task author"


class TaskAddSelfToMarkedUsersError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "You can not add yourself in marked users"


class MarkedUserNotFoundError(BaseException):
    def __init__(self, username: str = None):
        self.status_code = status.HTTP_400_BAD_REQUEST
        if username:
            self.detail = f"Marked user with username {username!r} not found"
        else:
            self.detail = f"Marked user not found"


class TaskReadPermissionDeniedError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You are not author or marked user"


class NotAuthorOfTaskUpdateError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You are not author of the task"


class TaskSelfMarkUpdateError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "You can not add yourself in marked users"


# Status Exceptions
class StatusNotFound(BaseException):
    def __init__(self, id: int = None):
        self.status_code = status.HTTP_400_BAD_REQUEST
        if id:
            self.detail = f"Status with id {id!r} not found"
        else:
            self.detail = "Status not found"


class NotSuperUserStatusCreateDeleteUpdateError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You do not have permission to modify or create statuses"


# Comment Exceptions
class CommentNotFoundError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "Comment not found"


class NotAuthorCommentReadError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You are not comment author"


class NotAuthorOrMarkedUserAddCommentError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You are not an author or a marked user"


class NotAuthorDeleteCommentError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You are not the author of the comment"


class CommentCreateLenError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Max len of text is 1000 symbols"


class NotAuthorCommentUpdateError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_403_FORBIDDEN
        self.detail = "You are not the author of the comment"
