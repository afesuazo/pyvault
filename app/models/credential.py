from datetime import datetime
from typing import Optional

from app.models.user import UserRead
from sqlmodel import Field, Relationship, SQLModel

# Data only model
from app.models.site import SiteRead


class CredentialBase(SQLModel):
    nickname: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    encrypted_password: str
    favorite: bool = Field(default=False)


class Credential(CredentialBase, table=True):
    __tablename__ = "credential"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)

    site: Optional["Site"] = Relationship(back_populates="credentials", sa_relationship_kwargs={'lazy': 'selectin'})
    site_id: Optional[int] = Field(foreign_key="site.id", nullable=True)

    # Owner of the credential
    owner: "User" = Relationship(back_populates="credentials", sa_relationship_kwargs={'lazy': 'selectin'})


# User id has to be provided when creating a credential
class CredentialCreate(CredentialBase):
    user_id: int
    site_id: Optional[int] = None


class CredentialUpdate(CredentialBase):
    site_id: Optional[int] = None


class CredentialRead(CredentialBase):
    created_at: datetime
    id: int
    site: Optional[SiteRead]
    owner: UserRead
