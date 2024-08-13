from httpx import AsyncClient

from tests.conftest import client


def test_user_register_success_status_code_201():
    response = client.post(
        "api/v1/auth/register/",
        json={
            "username": "user4",
            "first_name": "first_name4",
            "last_name": "last_name4",
            "email": "user4@example.com",
            "password": "12345678"
        }
    )
    assert response.status_code == 201


def test_user_login_success_status_code_200():
    response = client.post(
        "api/v1/auth/login/",
        json={
            "email": "user1@example.com",
            "password": "12345678"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_user_login_error_status_code_401():
    response = client.post(
        "api/v1/auth/login/",
        json={
            "email": "user2121123@example.com",
            "password": "1"
        }
    )
    assert response.status_code == 401


async def test_user_access_token_auth_success_status_code_200():
    response_token = client.post(
        "api/v1/auth/login/",
        json={
            "email": "user1@example.com",
            "password": "12345678"
        }
    )
    token = response_token.json()["access_token"]
    response = client.get(
        "api/v1/users/me/",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "user1"


def test_close_endpoint_without_token_error_status_code_403():
    response_not_valid_token = client.get(
        "api/v1/users/me/",
        headers={
            "Authorization": f"Bearer 13213123"
        }
    )
    response_without_token = client.get("api/v1/users/me/")
    assert response_not_valid_token.status_code == 401
    assert response_without_token.status_code == 403


def test_refresh_access_token_success_status_code_200():
    login_response = client.post(
        "api/v1/auth/login/",
        json={
            "email": "user1@example.com",
            "password": "12345678",
        }
    )
    refresh_token = login_response.json().get("refresh_token")
    refresh_access_token_response = client.post(
        "api/v1/auth/refresh/",
        headers={
            "Authorization": f"Bearer {refresh_token}"
        },
    )
    assert refresh_access_token_response.status_code == 200
    assert "access_token" in refresh_access_token_response.json()


def test_access_to_endpoint_with_refresh_token_error_status_code_401():
    login_response = client.post(
        "api/v1/auth/login/",
        json={
            "email": "user1@example.com",
            "password": "12345678",
        }
    )
    refresh_token = login_response.json().get("refresh_token")
    get_profile_response = client.get(
        "api/v1/users/me/",
        headers={
            "Authorization": f"Bearer {refresh_token}"
        }
    )
    assert get_profile_response.status_code == 401
