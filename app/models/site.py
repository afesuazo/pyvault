from typing import Optional

from sqlmodel import Field, SQLModel


# Data only model
class SiteBase(SQLModel):
    name: str
    url: Optional[str] = Field(default=None, unique=True)


class Site(SiteBase, table=True):
    __tablename__ = "site"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)

    # TODO: Add if sites get tied to each user
    # credentials: list["Credential"] = Relationship(back_populates="site", sa_relationship_kwargs={"cascade": "delete"})


# Created to differentiate from Base in docs


class SiteCreate(SiteBase):
    pass


class SiteUpdate(SiteBase):
    pass


class SiteRead(SiteBase):
    pass
