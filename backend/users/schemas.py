from typing import Optional
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    username: str
    first_name: str
    last_name: str


class UserRead(UserBase):
    id: int
    full_name: str
    avatar: Optional[str] = None
    about: Optional[str] = None


class UserProfileRead(UserRead):
    id: int
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    is_active: bool


class UserCreate(UserBase):
    email: EmailStr
    password: str


class UserUpdate(UserBase):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    about: Optional[str] = None
