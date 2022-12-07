from operator import or_
from typing import Optional, List

from fastapi import Depends
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.dependencies.db import get_db
from app.models.friendship import Friendship, FriendshipCreate, FriendshipUpdate


class FriendshipCRUD(BaseCRUD[Friendship, FriendshipCreate, FriendshipUpdate]):
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db_session = db_session

    async def create(self, friendship_data: FriendshipCreate) -> Friendship:
        friendship_dict = friendship_data.dict()
        friendship = Friendship(**friendship_dict)

        self.db_session.add(friendship)
        await self.db_session.commit()
        await self.db_session.refresh(friendship)

        return friendship

    async def read(self, unique_id: int) -> Optional[Friendship]:
        statement = select(Friendship).where(Friendship.uid == unique_id)
        results = await self.db_session.execute(statement=statement)

        # Scalar one or none allows empty results
        friendship = results.scalar_one_or_none()
        return friendship

    async def read_many(self, offset: int, limit: int, group_id: Optional[int]) -> List[Friendship]:
        if group_id:
            statement = select(Friendship).where(or_(Friendship.user_1_id == group_id, Friendship.user_2_id == group_id)).offset(offset).limit(limit)
        else:
            statement = select(Friendship).offset(offset).limit(limit)
        results = await self.db_session.execute(statement=statement)

        friendships = [r for r, in results.all()]
        return friendships

    async def update(self, unique_id: int, friendship_data: FriendshipUpdate) -> Friendship:
        friendship = await self.read(unique_id=unique_id)
        assert friendship is not None, f"friendship {unique_id} not found"
        values = friendship_data.dict()

        for k, v in values.items():
            setattr(friendship, k, v)

        self.db_session.add(friendship)
        await self.db_session.commit()
        await self.db_session.refresh(friendship)

        return friendship

    async def delete(self, unique_id: int) -> None:
        statement = delete(Friendship).where(Friendship.uid == unique_id)

        await self.db_session.execute(statement=statement)
        await self.db_session.commit()
