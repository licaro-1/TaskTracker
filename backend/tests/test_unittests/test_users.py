import pytest

from users.repository import UserRepository
from authentication.utils import hash_password
from users.models import User


@pytest.fixture(scope="session")
def user_repository():
    repository = UserRepository()
    return repository


@pytest.fixture(scope="session")
async def user(user_repository):
    password = "test_password"
    hashed_password = await hash_password(password)
    user = await user_repository.create_one({
        "username": "test_user",
        "first_name": "First",
        "last_name": "Last",
        "hashed_password": hashed_password,
        "email": "test_user@example.com",
    })
    return user


def test_success_create_object(user):
    assert user.username == "test_user"
    assert user.email == "test_user@example.com"
    assert user.first_name == "First"
    assert user.last_name == "Last"
    assert user.is_active
    assert not user.is_superuser


async def test_success_user_exists_by_email(user_repository: UserRepository, user: User):
    assert await user_repository.get_one(email=user.email)


async def test_success_user_exists_by_username(user_repository: UserRepository, user: User):
    assert await user_repository.get_one(username=user.username)


async def test_success_user_exists_by_first_name(user_repository: UserRepository, user: User):
    assert await user_repository.get_one(first_name=user.first_name)


async def test_success_user_exists_by_last_name(user_repository: UserRepository, user: User):
    assert await user_repository.get_one(last_name=user.last_name)


async def test_success_user_update(user_repository: UserRepository, user: User):
    upd_data = {
        "username": "updated_username",
        "first_name": "Upd First Name",
        "last_name": "Upd Last Name",
        "email": "upd@example.com"
    }
    user = await user_repository.update_one(id=user.id, data=upd_data)
    assert user.username == upd_data["username"]
    assert user.first_name == upd_data["first_name"]
    assert user.last_name == upd_data["last_name"]
    assert user.email == upd_data["email"]
    assert user.updated_at != user.created_at


async def test_success_user_delete(user_repository: UserRepository, user: User):
    await user_repository.delete_one(id=user.id)
    assert not await user_repository.get_one(id=user.id)


async def test_success_get_multi(user_repository: UserRepository, user: User):
    users_pages_count = 5
    result = await user_repository.get_multi(
        limit=1,
        offset=0
    )
    assert result["pages_count"] == users_pages_count
    assert "results" in result

