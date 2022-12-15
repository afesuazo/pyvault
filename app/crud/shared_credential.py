from typing import Optional, List

from fastapi import Depends
from sqlalchemy import delete, select
from sqlmodel import or_
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.dependencies.db import get_db
from app.models.credential import SharedCredential, SharedCredentialCreate, SharedCredentialUpdate


class SharedCredentialCRUD(BaseCRUD[SharedCredential, SharedCredentialCreate, SharedCredentialUpdate]):
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db_session = db_session

    async def create(self, credential_data: SharedCredentialCreate) -> SharedCredential:
        shared_credential_dict = credential_data.dict()
        shared_credential = SharedCredential(**shared_credential_dict)

        self.db_session.add(shared_credential)
        await self.db_session.commit()
        await self.db_session.refresh(shared_credential)

        return shared_credential

    async def read(self, unique_id: int) -> Optional[SharedCredential]:
        statement = select(SharedCredential).where(SharedCredential.uid == unique_id)
        results = await self.db_session.execute(statement=statement)

        # Scalar one or none allows empty results
        shared_credential = results.scalar_one_or_none()
        return shared_credential

    async def read_personal(self, unique_id: int, user_id: int, friend_id: Optional[int]) -> Optional[SharedCredential]:
        statement = select(SharedCredential).where(SharedCredential.uid == unique_id, SharedCredential.owner_id == user_id)
        results = await self.db_session.execute(statement=statement)

        # Scalar one or none allows empty results
        shared_credential = results.scalar_one_or_none()
        return shared_credential

    async def read_pair_personal(self, user_id: int, friend_id: int) -> Optional[SharedCredential]:
        statement = select(SharedCredential).where(SharedCredential.guest_id == friend_id, SharedCredential.owner_id == user_id)
        results = await self.db_session.execute(statement=statement)

        # Scalar one or none allows empty results
        shared_credential = results.scalar_one_or_none()
        return shared_credential

    async def read_personal_many(self, offset: int, limit: int, user_id: int, friend_id: Optional[int], owner: bool = True) -> List[SharedCredential]:
        if friend_id:
            if not owner:
                statement = select(SharedCredential).where(SharedCredential.owner_id == friend_id, SharedCredential.guest_id == user_id).offset(offset).limit(limit)
            else:
                statement = select(SharedCredential).where(SharedCredential.owner_id == user_id, SharedCredential.guest_id == friend_id).offset(offset).limit(limit)
        else:
            if not owner:
                statement = select(SharedCredential).where(SharedCredential.guest_id == user_id).offset(offset).limit(limit)
            else:
                statement = select(SharedCredential).where(SharedCredential.owner_id == user_id).offset(offset).limit(limit)

        results = await self.db_session.execute(statement=statement)

        shared_credentials = [r for r, in results.all()]
        return shared_credentials

    async def read_many(self, offset: int, limit: int, group_id: Optional[int]) -> List[SharedCredential]:
        if group_id:
            statement = select(SharedCredential).offset(offset).limit(limit)
        else:
            statement = select(SharedCredential).offset(offset).limit(limit)
        results = await self.db_session.execute(statement=statement)

        shared_credentials = [r for r, in results.all()]
        return shared_credentials

    async def update(self, unique_id: int, shared_credential_data: SharedCredentialUpdate) -> SharedCredential:
        shared_credential = await self.read(unique_id=unique_id)
        assert shared_credential is not None, f"credential {unique_id} not found"
        values = shared_credential_data.dict()

        for k, v in values.items():
            setattr(shared_credential, k, v)

        self.db_session.add(shared_credential)
        await self.db_session.commit()
        await self.db_session.refresh(shared_credential)

        return shared_credential

    async def delete(self, unique_id: int) -> None:
        statement = delete(SharedCredential).where(SharedCredential.uid == unique_id)

        await self.db_session.execute(statement=statement)
        await self.db_session.commit()
