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



@pytest.mark.asyncio
async def test_register_duplicate_user_raises_error(client: AsyncClient) -> None:
    await client.post("/auth/register", json={"username": "test_user_primary", "email": "primary@somemail.com", "password": "password_1"})
    response = await client.post("/auth/register", json={"username": "test_user_primary", "email": "secondary@somemail.com", "password": "password_2"})
    assert response.status_code == status.HTTP_409_CONFLICT


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
                             {"username": "test_user_0", "password": "test_password"}
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
async def test_get_current_user(client_populated_db: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    response = await client_populated_db.get("/auth/me", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json.get("username") == "test_superuser"


@pytest.mark.asyncio
async def test_get_current_user_with_invalid_token_raises_error(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/auth/me", headers={"Authorization": f"Bearer {123123}"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
