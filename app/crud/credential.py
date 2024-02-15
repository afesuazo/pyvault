from typing import Optional, List

from fastapi import Depends
from sqlalchemy import and_, delete, Delete, select, Select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.dependencies.db import get_db
from app.models.credential import Credential, CredentialCreate, CredentialUpdate


class CredentialCRUD(BaseCRUD[Credential, CredentialCreate, CredentialUpdate]):
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db_session = db_session

    async def _commit_refresh(self, instance: Credential):
        self.db_session.add(instance)
        await self.db_session.commit()
        await self.db_session.refresh(instance)
        return instance

    async def create(self, credential_data: CredentialCreate) -> Credential:
        credential = Credential(**credential_data.dict())
        return await self._commit_refresh(credential)

    # Reads a credential by its unique id regardless of the user, used for admin purposes
    async def read(self, unique_id: int) -> Optional[Credential]:
        statement: Select = select(Credential).where(Credential.id == unique_id).options(selectinload(Credential.site))
        results = await self.db_session.scalars(statement=statement)

        # one or none allows empty results
        credential = results.one_or_none()
        return credential

    # Does not require ownership, used for admin purposes
    async def read_many(self, offset: int, limit: int) -> List[Credential]:
        statement: Select = select(Credential).offset(offset).limit(limit)
        results = await self.db_session.scalars(statement=statement)

        credentials = [r for r, in results.all()]
        return credentials

    # Requires a user id to ensure ownership
    async def read_personal(self, unique_id: int, user_id: int) -> Optional[Credential]:
        statement: Select = select(Credential).where(
            and_(Credential.id == unique_id, Credential.user_id == user_id).options(
                selectinload(Credential.site))).options(selectinload(Credential.owner))
        results = await self.db_session.scalars(statement=statement)

        # one or none allows empty results
        credential = results.one_or_none()
        return credential

    # Requires a user id to ensure ownership
    async def read_personal_many(self, offset: int, limit: int, user_id: Optional[int], site_id: Optional[int]) -> List[
            Credential]:
        statement: Select = select(Credential).where(Credential.user_id == user_id).offset(offset).limit(limit).options(
            selectinload(Credential.site))

        # Site id allows for additional filtering when retrieving credentials
        if site_id:
            statement: Select = statement.where(Credential.site_id == site_id)

        results = await self.db_session.scalars(statement=statement)

        credentials = [r for r, in results.all()]
        return credentials

    async def update(self, unique_id: int, credential_data: CredentialUpdate) -> Credential:
        credential = await self.read(unique_id=unique_id)
        assert credential is not None, f"Credential {unique_id} not found"
        values = credential_data.dict()

        for k, v in values.items():
            setattr(credential, k, v)

        return await self._commit_refresh(credential)

    async def delete(self, unique_id: int) -> None:
        statement: Delete = delete(Credential).where(Credential.id == unique_id)
        await self.db_session.execute(statement=statement)
        await self.db_session.commit()
