from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship


# Data only model
class UserBase(SQLModel):
    email: str = Field(unique=True)
    username: str = Field(unique=True)
    first_name: str
    last_name: str
    hashed_password: str
    is_active: bool = Field(default=True)

    credentials: List["CredentialBase"] = Relationship(back_populates="user")


class User(UserBase, table=True):
    __tablename__ = "users"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs

class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass
