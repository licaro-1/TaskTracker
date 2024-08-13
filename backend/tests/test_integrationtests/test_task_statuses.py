from httpx import AsyncClient

from tasks.repository import TaskRepository, TaskStatusRepository
from tests.conftest import client


def test_task_status_create_success_status_code_201(superuser_token: str):
    response_create = client.post(
        "api/v1/task-statuses/",
        headers={
            "Authorization": f"Bearer {superuser_token}"
        },
        json={
            "name": "Test status",
            "slug": "Test"
        }
    )
    assert response_create.status_code == 201


def test_task_status_create_not_superuser_error_status_code_403(users_tokens: dict):
    user_token = users_tokens["user1"]["access_token"]
    response_create = client.post(
        "api/v1/task-statuses/",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
        json={
            "name": "Test status",
            "slug": "Test"
        }
    )
    assert response_create.status_code == 403


def test_get_task_statuses_success_status_code_200(users_tokens: dict):
    user_token = users_tokens["user1"]["access_token"]
    response = client.get(
        "api/v1/task-statuses/",
        headers={
            "Authorization": f"Bearer {user_token}"
        }
    )
    assert response.status_code == 200


def test_update_task_status_success_status_code_200(superuser_token: str):
    status_id_to_edit = 5
    response_update = client.patch(
        f"api/v1/task-statuses/{status_id_to_edit}/",
        headers={
            "Authorization": f"Bearer {superuser_token}"
        },
        json={
            "name": "Test status (updated)",
            "slug": "Test (updated)"
        }
    )
    assert response_update.status_code == 200


def test_update_task_status_not_superuser_error_status_code_403(users_tokens: dict):
    status_id_to_edit = 5
    user_token = users_tokens["user1"]["access_token"]
    response_update = client.patch(
        f"api/v1/task-statuses/{status_id_to_edit}/",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
        json={
            "name": "Test status (updated)",
            "slug": "Test (updated)"
        }
    )
    assert response_update.status_code == 403


def test_delete_task_status_success_status_code_204(superuser_token: str):
    status_id_to_delete = 5
    response_delete = client.delete(
        f"api/v1/task-statuses/{status_id_to_delete}/",
        headers={
            "Authorization": f"Bearer {superuser_token}"
        }
    )
    assert response_delete.status_code == 204


def test_delete_task_status_not_superuser_error_status_code_403(users_tokens: dict):
    status_id_to_delete = 5
    user_token = users_tokens["user1"]["access_token"]
    response_delete = client.delete(
        f"api/v1/task-statuses/{status_id_to_delete}/",
        headers={
            "Authorization": f"Bearer {user_token}"
        }
    )
    assert response_delete.status_code == 403


async def test_delete_task_status_when_it_used_in_tasks_status_code_200_tasks_status_update_to_open_success(
    ac: AsyncClient,
    users_tokens: dict,
    superuser_token: str
):
    status_for_delete = await TaskStatusRepository().create_one(data={"name": "Status for delete", "slug": "delete"})
    task = await TaskRepository().create_one(data={
        "author_id": 1,
        "status_id": status_for_delete.id,
        "title": "Task for status_delete",
        "description": "Task for status_delete",
        "marked_users": []
    })
    response_delete = await ac.delete(
        f"api/v1/task-statuses/{status_for_delete.id}/",
        headers={
            "Authorization": f"Bearer {superuser_token}"
        }
    )
    response_task = await ac.get(
        f"api/v1/tasks/{task.id}/",
        headers={
            "Authorization": f"Bearer {superuser_token}"
        }
    )
    assert response_delete.status_code == 204
    assert response_task.json()["status"]["id"] != status_for_delete.id
