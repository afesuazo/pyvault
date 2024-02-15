from typing import Optional, List

from fastapi import Depends
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.dependencies.db import get_db
from app.models.site import Site, SiteCreate, SiteUpdate


class SiteCRUD(BaseCRUD[Site, SiteCreate, SiteUpdate]):
    def __init__(self, db_session: AsyncSession = Depends(get_db)):
        self.db_session = db_session

    async def create(self, site_data: SiteCreate) -> Site:
        site_dict = site_data.dict()
        site = Site(**site_dict)

        self.db_session.add(site)
        await self.db_session.commit()
        await self.db_session.refresh(site)

        return site

    async def read(self, unique_id: int) -> Optional[Site]:
        statement = select(Site).where(Site.id == unique_id).options(selectinload(Site.credentials))
        results = await self.db_session.execute(statement=statement)

        # Scalar one or none allows empty results
        site = results.scalar_one_or_none()
        return site

    async def read_many(self, offset: int, limit: int, group_id: Optional[int] = None) -> List[Site]:
        statement = select(Site).offset(offset).limit(limit).options(selectinload(Site.credentials))
        results = await self.db_session.execute(statement=statement)

        sites = [r for r, in results.all()]
        return sites

    async def update(self, unique_id: int, site_data: SiteUpdate) -> Site:
        site = await self.read(unique_id=unique_id)
        assert site is not None, f"Site {unique_id} not found"
        values = site_data.dict()

        for k, v in values.items():
            setattr(site, k, v)

        self.db_session.add(site)
        await self.db_session.commit()
        await self.db_session.refresh(site)

        return site

    async def delete(self, unique_id: int) -> None:
        statement = delete(Site).where(Site.id == unique_id)

        await self.db_session.execute(statement=statement)
        await self.db_session.commit()
