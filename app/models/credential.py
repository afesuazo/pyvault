from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship


# Data only model
from app.models.site import SiteRead


class CredentialBase(SQLModel):
    nickname: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: str


class Credential(CredentialBase, table=True):
    __tablename__ = "credential"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.uid")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    favorite: bool = Field(default=False)
    site: Optional["Site"] = Relationship(back_populates="credentials", sa_relationship_kwargs={'lazy': 'selectin'})
    site_id: Optional[int] = Field(foreign_key="site.uid", nullable=True)


# Created to differentiate from Base in docs
class CredentialCreate(CredentialBase):
    user_id: int
    site_id: Optional[int]


class CredentialUpdate(CredentialBase):
    favorite: bool


class CredentialRead(CredentialBase):
    created_at: datetime
    uid: int
    site: Optional[SiteRead]

class SharedCredentialBase(SQLModel):
    credential_id: int = Field(foreign_key="credential.uid")

    owner_id: int = Field(foreign_key="user.uid")
    guest_id: int = Field(foreign_key="user.uid")


class SharedCredential(SharedCredentialBase, table=True):
    __tablename__ = "sharedCredentials"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs


class SharedCredentialCreate(SharedCredentialBase):
    pass


class SharedCredentialUpdate(SharedCredentialBase):
    pass
