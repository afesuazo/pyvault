from typing import Optional

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


# Data only model used by all CRUD operations
class UserBase(SQLModel):
    # Used for password recovery
    email: EmailStr = Field(unique=True)
    username: str = Field(unique=True)
    public_key: str


# Includes full model database representation
class User(UserBase, table=True):
    __tablename__ = "user"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    hashed_password: str


# Adds fields used only during registration
class UserCreate(UserBase):
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, value: str):
        # Constraint length, permit only alphanumeric
        if len(value) < 3 or len(value) > 20:
            raise ValueError('Username must be between 3 and 20 characters')
        if not value.isalnum():
            raise ValueError('Username must be alphanumeric')
        return value

    @field_validator('password')
    @classmethod
    def validate_password_lenght(cls, value: str):
        # Constraint length
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters')
        return value


# Allows for modifications of all base fields and password
class UserUpdate(UserBase):
    password: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_lenght(cls, value: str):
        # Constraint length
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters')
        return value


class UserRead(UserBase):
    pass
