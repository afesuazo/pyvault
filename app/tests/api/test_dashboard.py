from app.tests.conftest import db_site_quantity, db_credential_quantity
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
async def test_create_site(client_populated_db: AsyncClient, site_data: dict[str]) -> None:
    response = await client_populated_db.post("/dashboard/sites", json=site_data)
    assert response.status_code == status.HTTP_201_CREATED
    site_id = response.json()["id"]
    response = await client_populated_db.get(f"/dashboard/sites/{site_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["name"] == "site_5"


@pytest.mark.parametrize("site_data",
                         [
                             {"name": "", "url": "www.site5.com"},
                             {"url": "www.site5.com"},
                             {}
                         ])
@pytest.mark.asyncio
async def test_create_site_with_invalid_credentials_throws_error(client_populated_db: AsyncClient, site_data: dict[str]) -> None:
    response = await client_populated_db.post("/dashboard/sites", json=site_data)
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

@pytest.mark.asyncio
async def test_create_credential(client: AsyncClient) -> None:
    pass


@pytest.mark.asyncio
async def test_create_credential_with_invalid_data_throws_error(client: AsyncClient) -> None:
    pass


@pytest.mark.asyncio
async def test_get_credential_list(client: AsyncClient) -> None:
    pass


@pytest.mark.asyncio
async def test_get_credential_by_id(client: AsyncClient) -> None:
    pass


@pytest.mark.asyncio
async def test_get_credential_by_str_id_throws_error(client: AsyncClient) -> None:
    pass


@pytest.mark.asyncio
async def test_delete_credential(client: AsyncClient) -> None:
    pass
