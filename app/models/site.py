from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


# Data only model
class SiteBase(SQLModel):
    name: str


class Site(SiteBase, table=True):
    __tablename__ = "site"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)
    url: Optional[str] = Field(default=None, unique=True)

    # TODO: Add if sites get tied to each user
    credentials: list["Credential"] = Relationship(back_populates="site",
                                                   sa_relationship_kwargs={"cascade": "delete", 'lazy': 'selectin'})


# Created to differentiate from Base in docs


class SiteCreate(SiteBase):
    url: Optional[str]


class SiteUpdate(SiteBase):
    pass


class SiteRead(SiteBase):
    url: Optional[str]
    uid: int


class SiteSimpleRead(SiteBase):
    uid: int
