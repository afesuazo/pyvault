from fastapi import status
from httpx import AsyncClient
import pytest


@pytest.mark.parametrize("credentials",
                         [
                             {"username": "test_user_primary", "email": "primary@somemail.com",
                              "password": "password_1"},
                             {"username": "test_user_secondary", "email": "secondary@somemail.com",
                              "password": "password_2"}
                         ])
@pytest.mark.asyncio
async def test_register_new_user(client: AsyncClient, credentials: dict[str]) -> None:
    response = await client.post("/auth/register", json=credentials)
    assert response.status_code == status.HTTP_201_CREATED
    response_json = response.json()
    assert response_json.get("private_key") is not None
    assert response_json.get("public_key") is not None
    assert response_json.get("username") == credentials.get("username")


@pytest.mark.parametrize("credentials",
                         [
                             {"username": "test_user_primary", "email": "primary@somemail.com",
                              "password": "password_1"},
                             {"username": "test_user_primary", "email": "secondary@somemail.com",
                              "password": "password_2"}
                         ])
@pytest.mark.asyncio
async def test_register_duplicate_user_raises_error(client: AsyncClient, credentials: dict[str]) -> None:
    response = await client.post("/auth/register", json=credentials)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("credentials",
                         [
                             {"username": "test_user_primary", "email": "invalid.com",
                              "password": "password_1"},
                             {"username": "test_user_primary", "email": "secondary@somemail.com",
                              "password": "short"}
                         ])
@pytest.mark.asyncio
async def test_register_user_with_invalid_credentials_raises_error(client: AsyncClient, credentials: dict[str]) -> None:
    response = await client.post("/auth/register", json=credentials)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_register_user_with_empty_data_raises_error(client: AsyncClient) -> None:
    response = await client.post("/auth/register", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("credentials",
                         [
                             {"username": "test_user", "password": "test_password"}
                         ])
@pytest.mark.asyncio
async def test_login_user(client_populated_db: AsyncClient, credentials: dict[str]) -> None:
    response = await client_populated_db.post("/auth/login", data=credentials)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json.get("access_token") is not None


@pytest.mark.parametrize("credentials",
                         [
                             {"username": "test_user", "password": "invalid_password"}
                         ])
@pytest.mark.asyncio
async def test_login_user_with_invalid_credentials_raises_error(client_populated_db: AsyncClient, credentials: dict[str]) -> None:
    response = await client_populated_db.post("/auth/login", data=credentials)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    response_json = response.json()
    assert "Incorrect" in response_json.get("detail")


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient) -> None:
    pass


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token_raises_error(client: AsyncClient) -> None:
    pass
