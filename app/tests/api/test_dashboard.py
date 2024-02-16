from typing import Any

from app.tests.conftest import db_site_quantity, db_credential_quantity, db_user_quantity
from fastapi import status
from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_ping(client: AsyncClient) -> None:
    response = await client.get("/dashboard/ping")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"ping": "pong!"}


# ----------------- Sites -----------------


@pytest.mark.asyncio
async def test_get_site_list(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/dashboard/sites")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == db_site_quantity
    assert response.json()[0]["name"] == "Site_0"


@pytest.mark.asyncio
async def test_get_site_list_negative_limit(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/dashboard/sites?offset=0&limit=-5")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_site_list_negative_offset(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/dashboard/sites?offset=-10&limit=50")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_get_site_list_reduced_details(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/dashboard/sites/reduced")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == db_site_quantity
    assert "url" not in response.json()[0]


@pytest.mark.asyncio
async def test_get_site_list_when_none_exist_returns_empty_list(client: AsyncClient) -> None:
    response = await client.get("/dashboard/sites")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_get_site_by_id(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/dashboard/sites/2")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "Site_1"


@pytest.mark.asyncio
async def test_get_site_by_non_existing_id_return_none(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/dashboard/sites/5")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() is None


@pytest.mark.asyncio
async def test_get_site_by_str_id_throws_error(client_populated_db: AsyncClient) -> None:
    response = await client_populated_db.get("/dashboard/sites/five")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("site_data",
                         [
                             {"name": "site_5", "url": "www.site5.com"},
                         ])
@pytest.mark.asyncio
async def test_create_site(client: AsyncClient, site_data: dict[str]) -> None:
    response = await client.post("/dashboard/sites", json=site_data)
    assert response.status_code == status.HTTP_201_CREATED
    site_id = response.json()["id"]
    response = await client.get(f"/dashboard/sites/{site_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "site_5"


@pytest.mark.parametrize("site_data",
                         [
                             {"name": "", "url": "www.site5.com"},
                             {"url": "www.site5.com"},
                             {}
                         ])
@pytest.mark.asyncio
async def test_create_site_with_invalid_credentials_throws_error(client: AsyncClient, site_data: dict[str]) -> None:
    response = await client.post("/dashboard/sites", json=site_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.parametrize("site_data",
                         [
                             {"name": "Site_1", "url": "www.site1.com"},
                         ])
@pytest.mark.asyncio
async def test_create_duplicate_site_throws_error(client_populated_db: AsyncClient, site_data: dict[str]) -> None:
    response = await client_populated_db.post("/dashboard/sites", json=site_data)
    assert response.status_code == status.HTTP_409_CONFLICT


# ----------------- Credentials -----------------

@pytest.mark.parametrize("credential_data",
                         [
                             {
                                 "nickname": "credential_1",
                                 "email": "test_user_1@gmail.com",
                                 "username": "test_username",
                                 "encrypted_password": "pass_pass",
                                 "favorite": False,
                                 "user_id": 1,
                                 "site_id": 1
                             },
                             {
                                 "nickname": "credential_2",
                                 "email": "test_user_2@gmail.com",
                                 "username": "test_username",
                                 "encrypted_password": "pass_pass",
                                 "favorite": False,
                                 "user_id": 2,
                                 "site_id": 2
                             },
                         ])
@pytest.mark.asyncio
async def test_create_credential(client_populated_db: AsyncClient, superuser_token_headers: dict[str, str],
                                 credential_data: dict[str, Any]) -> None:
    response = await client_populated_db.post("/dashboard/credentials", json=credential_data, headers=superuser_token_headers)
    assert response.status_code == status.HTTP_201_CREATED

    credential_id = response.json()["id"]

    response = await client_populated_db.get(f"/dashboard/credentials/{credential_id}", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nickname"] == credential_data["nickname"]
    assert response.json()["encrypted_password"] != credential_data["encrypted_password"]


# Test no password, no nickname, non-existing site
@pytest.mark.parametrize("credential_data",
                         [
                             {
                                 "nickname": "credential_1",
                                 "email": "test_user_1@gmail.com",
                                 "username": "test_username",
                                 "encrypted_password": "",
                                 "favorite": False,
                                 "site_id": 1
                             },
                             {
                                 "nickname": "",
                                 "email": "test_user_2@gmail.com",
                                 "username": "test_username",
                                 "encrypted_password": "pass_pass",
                                 "favorite": False,
                                 "site_id": 2
                             },
                             {
                                 "nickname": "credential_2",
                                 "email": "test_user_2@gmail.com",
                                 "username": "test_username",
                                 "encrypted_password": "pass_pass",
                                 "favorite": False,
                                 "site_id": 2
                             },
                             {
                                 "nickname": "credential_2",
                                 "email": "test_user_2@gmail.com",
                                 "username": "test_username",
                                 "encrypted_password": "pass_pass",
                                 "favorite": False,
                                 "site_id": 6
                             },
                         ])
@pytest.mark.asyncio
async def test_create_credential_with_invalid_data_throws_error(client_populated_db: AsyncClient,
                                                                superuser_token_headers: dict[str, str],
                                                                credential_data: dict[str]) -> None:
    response = await client_populated_db.post("/dashboard/credentials", json=credential_data, headers=superuser_token_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_get_credential_list(client_populated_db: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    response = await client_populated_db.get("/dashboard/credentials", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == int(db_credential_quantity / db_user_quantity)
    assert response.json()[0]["nickname"] == "Credential0"


@pytest.mark.asyncio
async def test_get_credential_by_id(client_populated_db: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    response = await client_populated_db.get("/dashboard/credentials/1", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nickname"] == "Credential0"


@pytest.mark.asyncio
async def test_get_non_existent_credential_return_informative_error(client_populated_db: AsyncClient,
                                                                    superuser_token_headers: dict[str, str]) -> None:
    response = await client_populated_db.get("/dashboard/credentials/10", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_get_credential_by_str_id_throws_error(client_populated_db: AsyncClient,
                                                     superuser_token_headers: dict[str, str]) -> None:
    response = await client_populated_db.get("/dashboard/credentials/three", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_delete_credential(client_populated_db: AsyncClient, superuser_token_headers: dict[str, str]) -> None:
    response = await client_populated_db.delete("/dashboard/credentials/1", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_200_OK
    response = await client_populated_db.get("/dashboard/credentials/1", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_non_existent_credential_return_informative_error(client_populated_db: AsyncClient,
                                                                       superuser_token_headers: dict[str, str]) -> None:
    response = await client_populated_db.delete("/dashboard/credentials/10", headers=superuser_token_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
