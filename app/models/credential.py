from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


# Data only model

class CredentialBase(SQLModel):
    nickname: str = Field(index=True, unique=True)
    email: Optional[str] = Field(default=None)
    username: Optional[str] = Field(default=None)
    password: str

    user_id: int = Field(foreign_key="users.uid")
    site_id: Optional[int] = Field(default=0, foreign_key="sites.uid")


class Credential(CredentialBase, table=True):
    __tablename__ = "credentials"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs


class CredentialCreate(CredentialBase):
    pass


class CredentialUpdate(CredentialBase):
    pass


class SharedCredentialBase(SQLModel):
    credential_id: int = Field(foreign_key="credentials.uid")

    owner_id: int = Field(foreign_key="users.uid")
    guest_id: int = Field(foreign_key="users.uid")


class SharedCredential(SharedCredentialBase, table=True):
    __tablename__ = "sharedCredentials"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs


class SharedCredentialCreate(SharedCredentialBase):
    pass


class SharedCredentialUpdate(SharedCredentialBase):
    pass
