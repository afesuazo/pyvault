from typing import Optional, List

from fastapi import Depends
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.auth_utils import get_hashed_password
from app.crud.base import BaseCRUD
from app.dependencies.db import get_db
from app.models.user import User, UserCreate, UserUpdate


class UserCRUD(BaseCRUD[User, UserCreate, UserUpdate]):
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db_session = db_session

    # Private helper method to commit and refresh the instance
    async def _commit_refresh(self, instance: User):
        self.db_session.add(instance)
        await self.db_session.commit()
        await self.db_session.refresh(instance)
        return instance

    async def create(self, user_data: UserCreate) -> User:
        # Hash the password before saving so the server doesn't store plaintext passwords
        user = User(
            **user_data.dict(exclude={"password"}),
            hashed_password=get_hashed_password(user_data.password)
        )
        return await self._commit_refresh(user)

    async def read(self, unique_id: int) -> Optional[User]:
        statement = select(User).where(User.id == unique_id)
        results = await self.db_session.exec(statement=statement)

        # one or none allows empty results
        user = results.one_or_none()
        return user

    async def read_by_username(self, username: str) -> Optional[User]:
        statement = select(User).where(User.username == username)
        results = await self.db_session.exec(statement=statement)

        # one or none allows empty results
        user = results.one_or_none()
        return user

    async def read_by_email(self, email: str) -> Optional[User]:
        statement = select(User).where(User.email == email)
        results = await self.db_session.exec(statement=statement)

        # one or none allows empty results
        user = results.one_or_none()
        return user

    async def read_many(self, offset: int, limit: int) -> List[User]:
        statement = select(User).offset(offset).limit(limit)
        results = await self.db_session.exec(statement=statement)

        # users = [r for r, in results.all()]
        return results.all()

    async def update(self, unique_id: int, user_data: UserUpdate) -> User:
        user = await self.read(unique_id=unique_id)
        assert user is not None, f"User {unique_id} not found"

        # Get only the values that are set and update the user object
        values = user_data.dict(exclude_unset=True)

        # If the password is being updated, it needs to be hashed
        if 'password' in values:
            hashed_password = get_hashed_password(values['password'])
            del values['password']
            values['hashed_password'] = hashed_password

        for k, v in values.items():
            setattr(user, k, v)

        return await self._commit_refresh(user)

    async def delete(self, unique_id: int) -> None:
        statement = delete(User).where(User.id == unique_id)
        await self.db_session.execute(statement=statement)
        await self.db_session.commit()
