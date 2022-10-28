from typing import Optional

from sqlmodel import Field, SQLModel


# Data only model
class SiteBase(SQLModel):
    name: str
    url: Optional[str] = Field(default=None)


class Site(SiteBase, table=True):
    __tablename__ = "sites"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs


class SiteCreate(SiteBase):
    pass


class SiteUpdate(SiteBase):
    pass
