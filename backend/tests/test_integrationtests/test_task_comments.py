from tests.conftest import client


def test_comment_create_success_status_code_201(users_tokens: dict):
    comment_author_username = "user2"
    task_id = 1
    comment_data = {
        f"text": f"Comment by {comment_author_username}"
    }
    comment_author_token = users_tokens[comment_author_username]["access_token"]
    response = client.post(
        f"api/v1/task-comments/{task_id}/",
        headers={
            "Authorization": f"Bearer {comment_author_token}"
        },
        json=comment_data
    )
    assert response.status_code == 201


def test_comment_update_by_author_success_status_code_200(users_tokens: dict):
    comment_author_username = "user2"
    comment_author_token = users_tokens[comment_author_username]["access_token"]
    comment_id = 1
    task_id = 1
    upd_comment_data = {
        "text": "Updated comment"
    }
    response = client.patch(
        f"api/v1/task-comments/{comment_id}/",
        headers={
            "Authorization": f"Bearer {comment_author_token}"
        },
        json=upd_comment_data
    )
    response_get_task = client.get(
        f"api/v1/tasks/{task_id}/",
        headers={
            "Authorization": f"Bearer {comment_author_token}"
        }
    )
    response_get_task_data = response_get_task.json()
    assert response.status_code == 200
    assert response_get_task_data["comments"][0]["text"] == upd_comment_data["text"]


def test_delete_comment_by_author_success_status_code_204(users_tokens: dict):
    comment_author_username = "user2"
    comment_author_token = users_tokens[comment_author_username]["access_token"]
    comment_id = 1
    response = client.delete(
        f"api/v1/task-comments/{comment_id}/",
        headers={
            "Authorization": f"Bearer {comment_author_token}"
        }
    )
    assert response.status_code == 204

