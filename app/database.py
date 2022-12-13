from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel  # noqa  # Imported here to gather model metadata

# Using a local file at the time, will migrate to postgresql
# TODO: Move to config.toml when production DB is added
DATABASE_URL = f"sqlite+aiosqlite:///passwords.db"


class PasswordDB:
    def __init__(self) -> None:
        self.engine: AsyncEngine = create_async_engine(DATABASE_URL)
        self.async_session: sessionmaker[AsyncSession] = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initiate_db(self) -> None:
        # While testing this will drop and create all tables at startup
        async with self.engine.begin() as conn:
            # TODO: Remove once testing phase is done
            # await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)