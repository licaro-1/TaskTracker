import io
import os

from PIL import Image
from core.settings import STATIC_USER_IMAGES_ROOT
from tests.conftest import client


def test_users_list_success_status_code_200():
    response = client.get(
        "api/v1/users/"
    )
    assert response.status_code == 200


def test_users_list_correct_count_results():
    response = client.get(
        "api/v1/users/"
    )
    len_results = len(response.json()["results"])
    users_count = 5
    assert len_results == users_count


def test_users_list_pagination_params():
    users_on_page_limit = 1
    response = client.get(
        f"api/v1/users/?limit={users_on_page_limit}"
    )
    data = response.json()
    assert len(data["results"]) == users_on_page_limit
    assert data["pages_count"] == 5


def test_get_one_user_success_status_code_200():
    username = "user1"
    response = client.get(
        f"api/v1/users/@{username}/"
    )
    assert response.status_code == 200
    assert response.json()["username"] == username


def test_get_one_user_error_status_code_404():
    response = client.get(
        "api/v1/users/@123232/"
    )
    assert response.status_code == 404


def test_user_profile_success_status_code_200():
    access_token_response = client.post(
        "api/v1/auth/login/",
        json={
            "email": "user1@example.com",
            "password": "12345678"
        }
    )
    access_token = access_token_response.json()["access_token"]
    response = client.get(
        "api/v1/users/me/",
        headers={
            "Authorization": f"Bearer {access_token}",
        }
    )
    assert response.status_code == 200


def test_update_user_profile_success_status_code_200():
    response_token = client.post(
        "api/v1/auth/login/",
        json={
            "email": "user3@example.com",
            "password": "12345678"
        }
    )
    access_token = response_token.json()["access_token"]
    upd_data = {
        "first_name": "edit_first_name3",
        "last_name": "edit_last_name3"
    }
    patch_response = client.patch(
        "api/v1/users/me/",
        json={
            "first_name": upd_data["first_name"],
            "last_name": upd_data["last_name"]
        },
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["first_name"] == upd_data["first_name"]


def test_update_user_avatar_success_status_code_200(users_tokens):
    image = Image.new("RGB", (200, 200), "black")
    image_url = "tests/avatar.jpg"
    image.save(image_url)
    user_token = users_tokens["user1"].get("access_token")
    with open(image_url, "rb") as f:
        image_data = io.BytesIO(f.read())
        response = client.patch(
            "api/v1/users/me/update-avatar/",
            headers={
                "Authorization": f"Bearer {user_token}"
            },
            files={"image": ("avatar.jpg", image_data, "image/jpeg")}
        )
    upd_avatar = response.json()["avatar"]
    os.remove(image_url)
    os.remove(STATIC_USER_IMAGES_ROOT + f"/{upd_avatar}")
    assert response.status_code == 200
    assert upd_avatar

