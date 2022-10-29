from typing import Optional, List

from fastapi import Depends
from sqlalchemy import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.dependencies.db import get_db
from app.models.credential import Credential, CredentialCreate, CredentialUpdate


class CredentialCRUD(BaseCRUD[Credential, CredentialCreate, CredentialUpdate]):
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db_session = db_session

    async def create(self, credential_data: CredentialCreate) -> Credential:
        credential_dict = credential_data.dict()
        credential = Credential(**credential_dict)

        self.db_session.add(credential)
        await self.db_session.commit()
        await self.db_session.refresh(credential)

        return credential

    async def read(self, unique_id: int) -> Optional[Credential]:
        statement = select(Credential).where(Credential.uid == unique_id)
        results = await self.db_session.execute(statement=statement)

        # Scalar one or none allows empty results
        credential = results.scalar_one_or_none()
        return credential

    async def read_many(self, offset: int, limit: int, group_id: Optional[int]) -> List[Credential]:
        if group_id:
            statement = select(Credential).where(Credential.site_id == group_id).offset(offset).limit(limit)
        else:
            statement = select(Credential).offset(offset).limit(limit)
        results = await self.db_session.execute(statement=statement)

        credentials = [r for r, in results.all()]
        return credentials

    async def update(self, unique_id: int, credential_data: CredentialUpdate) -> Credential:
        credential = await self.read(unique_id=unique_id)
        assert credential is not None, f"credential {unique_id} not found"
        values = credential_data.dict()

        for k, v in values.items():
            setattr(credential, k, v)

        self.db_session.add(credential)
        await self.db_session.commit()
        await self.db_session.refresh(credential)

        return credential

    async def delete(self, unique_id: int) -> None:
        statement = delete(Credential).where(Credential.uid == unique_id)

        await self.db_session.execute(statement=statement)
        await self.db_session.commit()
