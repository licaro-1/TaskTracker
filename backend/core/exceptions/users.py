from fastapi import status

from .base import BaseException


class UserNotFoundError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = "User not found"

# User create errors


class UsernameAlreadyRegisteredError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Username already registered"


class EmailAlreadyRegisteredError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Email already registered"


class SmallUserPasswordError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_400_BAD_REQUEST
        self.detail = "Password must be at least 8 characters long"


# Login errors


class InvalidLoginDataError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Invalid username or password"


class UnauthorizedError(BaseException):
    def __init__(self, message: str = None):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        if message:
            self.detail = message
        else:
            self.detail = "Unauthorized"


class InvalidTokenError(BaseException):
    def __init__(self):
        self.status_code = status.HTTP_401_UNAUTHORIZED
        self.detail = "Invalid credentials"
