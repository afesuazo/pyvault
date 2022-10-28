from typing import Optional

from sqlmodel import Field, SQLModel


# Data only model
class CredentialBase(SQLModel):
    nickname: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: str

    site_id: Optional[int] = Field(default=None, foreign_key="sites.uid")


class Credential(CredentialBase, table=True):
    __tablename__ = "credentials"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs


class CredentialCreate(CredentialBase):
    pass


class CredentialUpdate(CredentialBase):
    pass
