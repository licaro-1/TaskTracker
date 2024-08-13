import json
from pathlib import Path

import pytest
from httpx import AsyncClient
from tests.conftest import client
from tests.conftest import prepare_database

from core.settings import BASE_DIR
from users.repository import UserRepository
from tasks.repository import TaskStatusRepository, TaskRepository


TEST_LOAD_DATA_PATH: Path = (
    BASE_DIR / "tests" / "test_integrationtests" / "test_load_data.json"
)


@pytest.fixture(scope="session", autouse=True)
def users_tokens(load_test_data_configuration):
    user_tokens = {}
    with open(TEST_LOAD_DATA_PATH) as f:
        users = json.load(f)["users"]
        for user in users:
            response_token = client.post(
                "api/v1/auth/login/",
                json={"email": user["email"], "password": user["password"]},
            )
            user_tokens[user["username"]] = {
                "access_token": response_token.json()["access_token"],
                "refresh_token": response_token.json()["refresh_token"],
            }
        return user_tokens


@pytest.fixture(scope="session", autouse=True)
async def load_test_data_configuration(ac: AsyncClient, prepare_database):
    """Crated users and task_statuses from load_data to db."""
    with open(TEST_LOAD_DATA_PATH, encoding="utf-8") as f:
        data = json.load(f)
        for user in data.get("users"):
            await UserRepository().create_one(user)
        for status in data.get("task_statuses"):
            await TaskStatusRepository().create_one(status)
        for task in data.get("tasks"):
            task["marked_users"] = [
                await UserRepository().get_one(username=username)
                for username in task["marked_users"]
            ]
            await TaskRepository().create_one(task)


@pytest.fixture(scope="session")
def superuser_token(ac: AsyncClient):
    """Get superuser access token."""
    admin_email = "admin@example.com"
    admin_password = "12345678"
    response = client.post(
        "api/v1/auth/login/", json={"email": admin_email, "password": admin_password}
    )
    return response.json()["access_token"]
