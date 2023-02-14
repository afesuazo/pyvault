from typing import AsyncGenerator

from aioredis import Redis, from_url


async def get_redis() -> AsyncGenerator[Redis, None]:
    """
    Yields redis object, used by FastApi "Depends"
    """

    session = from_url(f"redis://localhost")
    yield session