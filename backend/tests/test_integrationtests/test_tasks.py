from httpx import AsyncClient
from tests.conftest import client


def test_task_create_correct_success_status_code_201(users_tokens: dict):
    username = "user1"
    open_status_slug = "open"
    user_token = users_tokens[username]["access_token"]
    create_data = {
            "title": "Test Task Create Title",
            "description": "Test Task Create Description",
            "marked_users": []
        }
    response = client.post(
        "api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
        json=create_data
    )
    response_data = response.json()
    assert response.status_code == 201
    assert response_data["status"]["slug"] == open_status_slug
    assert response_data["author"]["username"] == username
    assert response_data["title"] == create_data["title"]
    assert response_data["description"] == create_data["description"]
    assert response_data["marked_users"] == create_data["marked_users"]


def test_get_tasks_success_status_code_200(users_tokens: dict):
    username = "user1"
    user_token = users_tokens[username]["access_token"]
    response = client.get(
        "api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
    )
    assert response.status_code == 200


def test_tasks_page_pagination_work_success(users_tokens: dict):
    tasks_on_page_limit = 1
    expected_pages_count = 3
    username = "user2"
    user_token = users_tokens[username]["access_token"]
    first_task_create_data = {
        "title": "First Task Title",
        "description": "First Task Description",
        "marked_users": []
    }
    second_task_create_data = {
        "title": "Second Task Title",
        "description": "Second Task Description",
        "marked_users": []
    }
    response_create_first_task = client.post(
        "api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
        json=first_task_create_data
    )
    response_create_seconds_task = client.post(
        "api/v1/tasks/",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
        json=second_task_create_data
    )
    response_one_task_on_page = client.get(
        f"api/v1/tasks/?limit={tasks_on_page_limit}",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
    )
    pagination_response_data = response_one_task_on_page.json()
    assert response_create_first_task.status_code == 201
    assert response_create_seconds_task.status_code == 201
    assert response_one_task_on_page.status_code == 200
    assert pagination_response_data["pages_count"] == expected_pages_count


def test_get_one_task_by_author_success_status_code_200(users_tokens: dict):
    task_author_username = "user1"
    task_id = 1
    user_token = users_tokens[task_author_username]["access_token"]
    response = client.get(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {user_token}"
        }
    )
    assert response.status_code == 200


def test_get_one_task_by_not_author_or_marked_user_error_status_code_403(users_tokens: dict):
    not_author_or_marked_user_username = "user1"
    task_id = 2
    user_token = users_tokens[not_author_or_marked_user_username]["access_token"]
    response = client.get(
        f"api/v1/tasks/{task_id}/",
        headers={
         "Authorization": f"Bearer {user_token}"
        }
    )
    assert response.status_code == 403


def test_update_task_by_author_correct_status_code_200(users_tokens: dict):
    author_username = "user1"
    marked_user_username = "user2"
    status_id_to_upd = 2
    task_id = 1
    user_token = users_tokens[author_username]["access_token"]
    update_data = {
        "title": "Updated Task Title",
        "description": "Updated Task Description",
        "status_id": status_id_to_upd,
        "marked_users": [marked_user_username]
    }
    response = client.put(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {user_token}"
        },
        json=update_data
    )
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["status"]["id"] == status_id_to_upd
    assert len(response_data["marked_users"]) == 1
    assert response_data["marked_users"][0]["username"] == marked_user_username


def test_marked_user_have_access_to_task_view(users_tokens: dict):
    marked_user_username = "user2"
    task_id = 1
    marked_user_token = users_tokens[marked_user_username]["access_token"]
    response = client.get(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {marked_user_token}"
        }
    )
    assert response.status_code == 200


def test_marked_user_have_no_access_to_update_task(users_tokens: dict):
    marked_user_username = "user2"
    task_id = 1
    marked_user_token = users_tokens[marked_user_username]["access_token"]
    response = client.put(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {marked_user_token}"
        },
        json={
            "title": "Title to update",
            "description": "Description to update",
            "status_id": 2,
            "marked_users": []
        }
    )
    assert response.status_code == 403


def test_update_task_marked_users_work_correct(users_tokens: dict):
    task_id = 1
    task_author_username = "user1"
    task_author_token = users_tokens[task_author_username]["access_token"]
    marked_user_names = ["user3", "user2"]
    response = client.put(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {task_author_token}"
        },
        json={
            "title": "Title to update",
            "description": "Description to update",
            "status_id": 2,
            "marked_users": marked_user_names
        }
    )
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data["marked_users"]) == len(marked_user_names)
    assert response_data["marked_users"][0]["username"] == marked_user_names[0]
    assert response_data["marked_users"][1]["username"] == marked_user_names[1]


def test_task_delete_by_author_success_status_code_204(users_tokens: dict):
    task_author_username = "user1"
    task_id = 1
    task_author_token = users_tokens[task_author_username]["access_token"]
    response = client.delete(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {task_author_token}"
        }
    )
    response_get_task = client.get(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {task_author_token}"
        }
    )
    assert response.status_code == 204
    assert response_get_task.status_code == 404


def test_task_delete_by_not_author_or_superuser_error_status_code_403(users_tokens: dict):
    username = "user1"
    task_id = 2
    task_author_token = users_tokens[username]["access_token"]
    response = client.delete(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {task_author_token}"
        }
    )
    assert response.status_code == 403