from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from app.models.user import UserBase


# Data only model

class CredentialBase(SQLModel):
    nickname: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: str

    user_id: int = Field(foreign_key="users.uid")
    user: Optional[UserBase] = Relationship(back_populates="credentials")
    site_id: Optional[int] = Field(default=0, foreign_key="sites.uid")


class Credential(CredentialBase, table=True):
    __tablename__ = "credentials"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs


class CredentialCreate(CredentialBase):
    pass


class CredentialUpdate(CredentialBase):
    pass
