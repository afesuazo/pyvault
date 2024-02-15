from typing import AsyncGenerator

import config
from app.core.auth_utils import get_hashed_password
from app.core.cypt_utils import generate_key_pair
from app.models.user import User, UserCreate, UserCreateInternal
from httpx import AsyncClient
import pytest

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.pool import StaticPool

from app.dependencies.db import get_db
from app.main import app


@pytest.fixture
async def loaded_db_session() -> AsyncGenerator[AsyncSession, None]:
    engine: AsyncEngine = create_async_engine(config.TEST_DB_URL, poolclass=StaticPool)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        test_user = UserCreateInternal(username="test_user",
                                       email="test_user@test.com",
                                       password="test_password",
                                       public_key=generate_key_pair()[0])
        test_user = User(
            **test_user.dict(exclude={"password"}),
            hashed_password=get_hashed_password(test_user.password)
        )

        session.add(test_user)
        await session.commit()
        await session.refresh(test_user)

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
