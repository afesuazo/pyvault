import config

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel  # noqa  # Imported here to gather model metadata


class PasswordDB:
    def __init__(self) -> None:
        # Maintains the connection pool and executes SQL queries
        self.engine: AsyncEngine = create_async_engine(config.DB_URL)
        # Used to manage independent sessions for each request. This allows the program to stage and buffer
        # transactions allowing for asynchronous execution
        self.async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initiate_db(self) -> None:
        async with self.engine.begin() as conn:
            if config.TESTING:
                # While testing this will drop and create all tables at startup
                await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
