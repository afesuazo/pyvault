from typing import AsyncGenerator, Any, Dict, Coroutine

import config
from app.core.auth_utils import get_hashed_password
from app.core.cypt_utils import generate_key_pair, encrypt_with_key
from app.models.credential import Credential
from app.models.site import Site
from app.models.user import User
from httpx import AsyncClient
import pytest

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool

from app.dependencies.db import get_db
from app.main import app

db_user_quantity = 5
db_site_quantity = 2
db_credential_quantity = 10

super_user_key_pair = generate_key_pair()
key_pairs = [generate_key_pair() for _ in range(db_user_quantity)]


def user_generator():
    for i in range(5):
        yield User(username=f'test_user_{i}',
                   email=f'test_user_{i}@gmail.com',
                   hashed_password=get_hashed_password("test_password"),
                   public_key=key_pairs[i][0])


def site_generator():
    for i in range(db_site_quantity):
        yield Site(name=f'Site_{i}', url=f'https://site{i}.com')


def credential_generator():
    # Create 2 credentials per user
    for i in range(db_credential_quantity):
        # user id and site id are 1-indexed in the db
        yield Credential(nickname=f'Credential{i}',
                         email=f'test_user_{i % db_user_quantity}@gmail.com',
                         username=f'test_user_{i % db_user_quantity}',
                         encrypted_password=encrypt_with_key(key_pairs[i % db_user_quantity][0], "test_password"),
                         user_id=(i % db_user_quantity) + 1,
                         site_id=(i % db_site_quantity) + 1)


async def get_superuser_token_headers(client: AsyncClient) -> dict[str, str]:
    login_data = {
        "username": 'test_superuser',
        "password": 'test_superuser_password'
    }
    response = await client.post(f"/auth/login", data=login_data)
    response_json = response.json()
    token = response_json["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return headers


@pytest.fixture
async def loaded_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine: AsyncEngine = create_async_engine(config.TEST_DB_URL, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:

        # Add a superuser to the database
        superuser = User(username="test_superuser",
                         email="test_superuser@gmail.com",
                         hashed_password=get_hashed_password("test_superuser_password"),
                         public_key=super_user_key_pair[0])
        session.add(superuser)
        await session.commit()
        await session.refresh(superuser)

        # Load test data into the test database
        for user in user_generator():
            session.add(user)
            await session.commit()
            await session.refresh(user)

        for site in site_generator():
            session.add(site)
            await session.commit()
            await session.refresh(site)

        for credential in credential_generator():
            session.add(credential)
            await session.commit()
            await session.refresh(credential)

        yield session


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine: AsyncEngine = create_async_engine(config.TEST_DB_URL, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def get_session_override() -> AsyncSession:
        return db_session

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        # dependency_overrides is a dict holding the current function (overridden) as
        # a key and the new functions as a value
        app.dependency_overrides[get_db] = get_session_override
        yield client
        # Clearing the dictionary resets all overrides
        app.dependency_overrides.clear()


@pytest.fixture
async def client_populated_db(loaded_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    def get_session_override() -> AsyncSession:
        return loaded_db_session

    async with AsyncClient(app=app, base_url="http://127.0.0.1:8000") as client:
        app.dependency_overrides[get_db] = get_session_override
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
async def superuser_token_headers(client_populated_db: AsyncClient) -> dict[str, str]:
    return await get_superuser_token_headers(client_populated_db)
