from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from pydantic import field_validator


# Data only model
class SiteBase(SQLModel):
    name: str = Field(unique=True)

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str):
        # Constraint length, permit only alphanumeric
        if len(value) < 3 or len(value) > 20:
            raise ValueError('Site name must be between 3 and 20 characters')
        return value



class Site(SiteBase, table=True):
    __tablename__ = "site"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    url: Optional[str] = Field(default=None, unique=True)

    # TODO: Add if sites get tied to each user
    credentials: list["Credential"] = Relationship(back_populates="site",
                                                   sa_relationship_kwargs={"cascade": "delete", 'lazy': 'selectin'})


class SiteCreate(SiteBase):
    url: Optional[str]


class SiteUpdate(SiteBase):
    pass


class SiteSimpleRead(SiteBase):
    id: int


class SiteRead(SiteSimpleRead):
    url: Optional[str]
